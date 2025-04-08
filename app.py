from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from fuzzywuzzy import process
import re
import math
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# --- FAQ Knowledge Base ---
faq_data = {

     # --- General Help and Information ---
    "Hello": "Hello there! How can I help you today?",
    "Hi": "Hi! What's on your mind?",
    "Hey": "Hey! Ready to chat?",
    "How are you?": "As an AI, I don't experience feelings, but I'm functioning optimally and ready to assist you!",
    "How's it going?": "Everything is running smoothly on my end. What can I do for you?",
    "What's up?": "Just processing information and ready for your questions!",
    "What can you do?": "I can answer your questions, provide information on a wide range of topics, explain concepts, help with basic tasks, and even try to have a little fun. Just ask!",
    "Thank you": "You're welcome!",
    "Thanks": "No problem!",
    "Goodbye": "Goodbye! Feel free to reach out if you have more questions later.",
    "Bye": "Bye!",
    "See you later": "See you later!",

    # --- Help for Kids and Students ---
    "Explain like I'm five, what is a computer?": "Imagine a super smart toy box that can remember lots of things (like stories and numbers) and can do special things when you tell it what to do!",
    "What is the solar system?": "The solar system is like our cosmic neighborhood! It has a big star in the middle called the Sun, and planets (like Earth!), moons, and other smaller objects that go around it.",
    "What is photosynthesis?": "Photosynthesis is like how plants eat! They use sunlight, water, and air to make their own food, and they also give us the air we breathe.",
    "What are the colors of the rainbow?": "The colors of the rainbow are Red, Orange, Yellow, Green, Blue, Indigo, and Violet. You can remember them with the silly name ROY G. BIV!",
    "Tell me a fun fact about animals": [
        "A starfish doesn't have a brain!",
        "Butterflies taste with their feet!",
        "Snails can sleep for three years!",
        "A group of flamingos is called a 'flamboyance'!"
    ],
    "Can you help me with my homework?": "I can try my best! What subject or question are you working on?",
    "Explain fractions simply": "Imagine you have a pizza. A fraction is like a piece of that pizza. The bottom number tells you how many slices the whole pizza was cut into, and the top number tells you how many slices you have.",
    "What is gravity?": "Gravity is like an invisible force that pulls things towards each other. It's why we stay on the ground and why things fall down, not up!",
    "Tell me a story": [
        "Once upon a time, in a land far away...",
        "A little seed dreamed of becoming a tall tree...",
        "The brave knight set off on a quest..."
    ],

    # --- Help for Others (General Information) ---
    "What is the capital of India?": "The capital of India is New Delhi.",
    "What is the current time in Bengaluru?": "The current time in Bengaluru, Karnataka, India is Tuesday, April 8, 2025 at 2:54 AM PST. (Please note that as a language model, my time might have a slight delay or be based on a different reference point.)",
    "What is the weather like in Bengaluru today?": "I do not have access to real-time weather information for your specific location. However, you can check a reliable weather app or website for the current conditions in Bengaluru.",
    "What are some popular tourist attractions in Bengaluru?": "Bengaluru is known for its gardens, tech industry, and historical sites. Some popular attractions include Lalbagh Botanical Garden, Cubbon Park, Bangalore Palace, Tipu Sultan's Summer Palace, and the Visvesvaraya Industrial and Technological Museum.",
    "How do I learn a new language?": "Learning a new language involves consistent practice, immersion (if possible), studying vocabulary and grammar, and not being afraid to make mistakes. There are many apps, online courses, and language exchange partners that can help.",
    "What are some tips for staying healthy?": "Staying healthy involves a balanced diet, regular exercise, getting enough sleep, managing stress, and staying hydrated.",
    "What is artificial intelligence?": "Artificial intelligence (AI) is a field of computer science that aims to create machines that can perform tasks that typically require human intelligence, such as learning, problem-solving, and decision-making.",
    "Tell me a fun fact": [
        "Bananas are berries, but strawberries aren't!",
        "The Eiffel Tower can be about 15 cm taller during the summer due to thermal expansion.",
        "Octopuses have three hearts!",
        "Honey never spoils."
    ],
    # --- Python ---
    "What is Python?": "Python is a high-level, interpreted, and general-purpose programming language known for its simplicity and readability.",
    "What are Python data types?": "Common Python data types include int, float, str, bool, list, tuple, set, and dict.",
    "What is a Python list?": "A list is a mutable, ordered collection of items, defined using square brackets [].",
    "What is a Python dictionary?": "A dictionary is an unordered collection of key-value pairs defined using curly braces {}.",
    "What is a function in Python?": "A function is a block of reusable code that performs a specific task and is defined using the 'def' keyword.",
    "What are Python decorators?": "Decorators are functions that modify the behavior of other functions or methods using the @ syntax.",
    "What is the difference between '==' and 'is' in Python?": "'==' checks value equality, while 'is' checks if two variables point to the same object in memory.",
    "What is list comprehension?": "List comprehension is a concise way to create lists using a single line of code.",
    "What is a lambda function?": "A lambda function is an anonymous function defined with the lambda keyword, useful for short, throwaway functions.",
    "How is exception handling done in Python?": "Exception handling uses try-except blocks to catch and handle errors gracefully.",
    "What is the use of the 'with' statement in Python?": "It simplifies exception handling and automatically manages resources, like opening and closing files.",
    "What is a Python tuple?": "A tuple is an immutable, ordered collection of items, defined using parentheses ().",
    "What is a Python set?": "A set is an unordered collection of unique elements, defined using curly braces {} or the set() constructor.",
    "What is a module in Python?": "A module is a file containing Python definitions and statements, which can be imported and used in other Python scripts.",
    "What is a package in Python?": "A package is a collection of Python modules organized in a directory hierarchy, allowing for better code organization.",
    "What is pip?": "Pip is the package installer for Python. It is used to install and manage third-party libraries and dependencies.",
    "What is a virtual environment in Python?": "A virtual environment is an isolated Python environment that allows you to install packages for a specific project without affecting other projects or the global Python installation.",
    "What are decorators used for in Python?": "Decorators are used to add functionality to functions or methods in a readable and reusable way.",
    "What is a generator in Python?": "A generator is a special type of function that returns an iterator, producing values on demand using the 'yield' keyword. This is memory-efficient for large sequences.",
    "What is list comprehension and how is it useful?": "List comprehension provides a concise way to create lists based on existing iterables. It's often more readable and efficient than traditional for loops for list creation.",
    "What is a lambda function and when should you use it?": "A lambda function is a small, anonymous function defined using the 'lambda' keyword. It's useful for short, throwaway functions, often used as arguments to higher-order functions.",
    "How does Python handle exceptions?": "Python uses 'try-except' blocks to handle exceptions (errors that occur during execution). The code that might raise an exception is placed in the 'try' block, and the code to handle the exception is in the 'except' block.",
    "What is the purpose of the 'finally' block in exception handling?": "The 'finally' block, if present, is always executed after the 'try' and 'except' blocks, regardless of whether an exception occurred or was handled. It's typically used for cleanup operations.",
    "What is Object-Oriented Programming (OOP) in Python?": "OOP is a programming paradigm based on the concept of 'objects,' which can contain data (attributes) and code (methods). Key OOP principles in Python include encapsulation, inheritance, and polymorphism.",
    "What is a class in Python?": "A class is a blueprint for creating objects. It defines the attributes and methods that objects of that class will have.",
    "What is an object in Python?": "An object is an instance of a class. It has its own set of attributes and can call the methods defined in its class.",
    "What is inheritance in OOP?": "Inheritance allows a class (subclass or derived class) to inherit attributes and methods from another class (superclass or base class), promoting code reuse.",
    "What is polymorphism in OOP?": "Polymorphism allows objects of different classes to respond to the same method call in their own way, providing flexibility and extensibility.",
    "What is encapsulation in OOP?": "Encapsulation is the bundling of data (attributes) and the methods that operate on that data within a single unit (a class). It helps in hiding the internal implementation details of an object.",
    "What is a decorator in the context of classes?": "Decorators can also be applied to methods within a class to modify their behavior.",
    "What are magic methods (dunder methods) in Python?": "Magic methods are special methods in Python that start and end with double underscores (e.g., '__init__', '__str__'). They define how objects behave in certain operations.",
    "What is the difference between static methods and class methods?": "Static methods are defined within a class but don't receive an instance or the class itself as an implicit first argument. Class methods receive the class itself as the first argument ('cls').",
    "What are properties in Python classes?": "Properties allow you to define getter, setter, and deleter methods for class attributes, providing a way to control attribute access and modification.",
    "What is the Global Interpreter Lock (GIL) in Python?": "The GIL is a mechanism in CPython (the most common Python implementation) that allows only one thread to hold control of the Python interpreter at any given time. This can limit the performance of multithreaded CPU-bound tasks.",
    "How can you achieve parallelism in Python despite the GIL?": "For CPU-bound tasks, you can use the 'multiprocessing' module, which creates separate processes with their own memory spaces, bypassing the GIL limitation.",
    "What is asynchronous programming in Python?": "Asynchronous programming allows you to perform multiple tasks seemingly concurrently by switching between them when one task is waiting for an I/O operation. The 'asyncio' module provides support for asynchronous programming using 'async' and 'await' keywords.",
    "What are regular expressions (regex) and how are they used in Python?": "Regular expressions are sequences of characters that define a search pattern. The 're' module in Python allows you to work with regex for tasks like pattern matching, searching, and substitution in strings.",
    "How do you work with files in Python?": "Python provides built-in functions like 'open()' to interact with files. You can read from files using methods like 'read()', 'readline()', and 'readlines()', and write to files using 'write()' and 'writelines()'. The 'with' statement is recommended for automatic resource management.",
    "What are some popular Python libraries for data science?": "Popular data science libraries in Python include NumPy for numerical computations, pandas for data manipulation and analysis, matplotlib and seaborn for data visualization, and scikit-learn for machine learning.",
    "What are some popular Python frameworks for web development?": "Popular web development frameworks in Python include Django (a high-level framework) and Flask (a microframework).",
    "How do you install and manage Python packages?": "Python packages are installed and managed using pip (Package Installer for Python). You can install packages from the Python Package Index (PyPI) using commands like 'pip install <package_name>'.",
     "What are metaclasses in Python?": "Metaclasses are the 'classes of classes'. They define how classes are created. By default, 'type' is the metaclass used to create all classes in Python. You can define custom metaclasses to control class creation behavior, such as enforcing specific attributes or methods.",
    "What are descriptors in Python and how are they used?": "Descriptors are objects that define how attributes of a class are accessed, set, or deleted. They implement at least one of the '__get__', '__set__', or '__delete__' methods. They are the mechanism behind properties, methods, and static/class methods.",
    "What are mixins in Python?": "Mixins are classes that provide specific functionality to other classes through multiple inheritance, without being considered a primary base class. They are often used to 'mix in' a set of methods to unrelated classes.",
    "What is the difference between abstract methods and abstract properties in Python?": "Abstract methods are methods declared in an abstract base class (using the 'abc' module and '@abstractmethod' decorator) but have no implementation. Subclasses must override them. Abstract properties are similar but for class attributes, using '@abstractproperty' and defining 'fget' (and optionally 'fset' and 'fdel').",
    "How does operator overloading work in Python?": "Operator overloading allows you to define how standard operators (like '+', '-', '*', '<', '==', etc.) behave when used with instances of your custom classes. This is achieved by implementing special 'magic' methods (e.g., '__add__', '__sub__', '__lt__', '__eq__').",
    "How does Python manage memory?": "Python uses automatic memory management through a mechanism called reference counting. When an object's reference count drops to zero, it becomes eligible for garbage collection. Python also has a garbage collector that handles cyclic references.",
    "What is profiling in Python and why is it important?": "Profiling is the process of measuring the execution time and resource usage of different parts of your Python code. It's crucial for identifying performance bottlenecks and optimizing your code.",
    "What are some tools for profiling Python code?": "Common Python profiling tools include 'cProfile' and 'profile' (built-in modules for detailed profiling), 'line_profiler' (for line-by-line profiling), and 'memory_profiler' (for memory usage analysis).",
    "What are Python C extensions and why might you use them?": "Python C extensions are modules written in C or C++ that can be imported and used in Python code. They are often used to achieve significant performance improvements for computationally intensive tasks by leveraging the speed of compiled languages.",
    "What is Cython?": "Cython is a programming language that is a superset of Python, allowing you to write C extensions more easily by annotating Python code with C data types. It can then be compiled into C code and further into a Python extension.",
    "What is dynamic code execution in Python?": "Python allows for dynamic execution of code using functions like 'exec()' (which executes Python code from strings or code objects) and 'eval()' (which evaluates a Python expression). These should be used cautiously due to potential security risks if the input is not trusted.",
    "What is introspection in Python?": "Introspection is the ability of an object to know about its own attributes and methods at runtime. Python provides built-in functions like 'type()', 'dir()', 'getattr()', 'setattr()', 'hasattr()', and the '__dict__' attribute to facilitate introspection.",
    "How can decorators be used for more advanced patterns?": "Advanced decorator usage includes class decorators (to modify entire classes), parameterized decorators (decorators that take arguments), and applying multiple decorators to a single function or method.",
    "What are some common design patterns used in Python?": "While Python's dynamic nature allows for flexible implementations, common design patterns like Factory, Singleton, Observer, Strategy, and Decorator (implemented using Python's decorator feature) are frequently used to structure code effectively.",
    "How do you package Python applications for distribution?": "Python applications can be packaged using tools like 'setuptools' (the standard) or 'poetry' and 'flit'. This involves creating a 'setup.py' file (or using configuration files for other tools) to define the package metadata and dependencies, allowing others to install your application easily.",
    "What is the purpose of virtual environments in deployment?": "Virtual environments ensure that your application's dependencies are isolated from the system-wide Python installation and other projects, preventing version conflicts and ensuring reproducible deployments.",
    "What is containerization with Docker and why is it used for Python applications?": "Docker is a platform for building, shipping, and running applications in isolated containers. Containerizing a Python application with Docker bundles the application and all its dependencies into a portable image, ensuring consistent execution across different environments (development, testing, production).",
    "How are Python applications typically deployed on cloud platforms like AWS, Google Cloud, or Azure?": "Deployment on cloud platforms often involves containerization (using Docker and services like AWS ECS/EKS, Google Cloud Run/Kubernetes Engine, Azure Container Instances/Kubernetes Service), serverless functions (AWS Lambda, Google Cloud Functions, Azure Functions), or managed application services (AWS Elastic Beanstalk, Google App Engine, Azure App Service).",
    "What are some advanced concurrency patterns beyond basic threading and multiprocessing?": "Advanced concurrency patterns include using asynchronous programming with 'asyncio' for I/O-bound tasks, utilizing thread pools and process pools for managing resources efficiently, and employing more sophisticated synchronization primitives like semaphores, events, and conditions for complex shared-state management.",
    "How do you work with different types of databases in advanced Python applications?": "Advanced database interaction often involves using Object-Relational Mappers (ORMs) like SQLAlchemy or Django ORM to abstract away the underlying SQL and provide a more Pythonic way to interact with relational databases. For NoSQL databases, specialized drivers like 'pymongo' for MongoDB are used, often with a focus on document-based data models.",
    "What are some advanced topics in web development with Python frameworks like Django or Flask?": "Advanced web development topics include building RESTful APIs, implementing authentication and authorization mechanisms (e.g., JWT, OAuth), handling web sockets, using message queues (e.g., Celery, RabbitMQ) for background tasks, optimizing database queries, and deploying scalable web applications.",
    "What are some advanced concepts in data science and machine learning with Python?": "Advanced topics include deep learning (using TensorFlow or PyTorch), natural language processing (NLP), time series analysis, advanced statistical modeling, model deployment, and working with big data technologies (e.g., Spark with PySpark).",
    "How can you optimize the performance of data-intensive Python applications?": "Optimization techniques include using efficient data structures (e.g., NumPy arrays, pandas DataFrames), leveraging vectorized operations, minimizing loops, using generators for large datasets, profiling code to identify bottlenecks, and potentially using compiled extensions for critical parts.",
    # --- Foundational Python Concepts (Deep Dive) ---
    "Explain the Python interpreter's workflow.": "The Python interpreter processes code line by line. It first compiles the source code into bytecode (a lower-level, platform-independent representation) and then executes this bytecode using the Python Virtual Machine (PVM). This compilation step is implicit and happens at runtime.",
    "Discuss the nuances of Python's dynamic typing.": "Python is dynamically typed, meaning you don't need to explicitly declare the data type of a variable. The type is inferred at runtime based on the value assigned. This offers flexibility but can also lead to runtime type errors if not handled carefully. Type hints (introduced in Python 3.5+) allow you to add optional type annotations for static analysis but don't enforce types at runtime in standard Python.",
    "Elaborate on the differences between mutable and immutable data types in Python with examples.": "Mutable data types (like lists, dictionaries, sets) can be modified after creation. Operations on them can change the object in place. Immutable data types (like integers, floats, strings, tuples) cannot be changed after creation. Any operation that seems to modify them actually creates a new object. Example: Appending to a list modifies the original list; string concatenation creates a new string.",
    "Explain the concept of namespaces and scope in Python (local, global, nonlocal).": "Namespaces are mappings from names to objects. Different namespaces can have the same name referring to different objects. Scope defines the region where a name is accessible. Python has local scope (within a function), global scope (at the module level), and nonlocal scope (for nested functions accessing variables in the enclosing function's scope). The LEGB rule (Local, Enclosing function locals, Global, Built-in) determines the order in which Python searches for a name.",
    "Describe Python's handling of truthiness and falsiness.": "In Python, every object has a boolean value. By default, most objects are considered 'truthy'. Values considered 'falsy' include 'False', 'None', zero of any numeric type (0, 0.0, 0j), empty sequences ([], (), ''), empty mappings ({}), and sets (set()). Custom objects can define their truthiness by implementing the '__bool__()' or '__len__()' methods.",
    "Discuss the different ways to pass arguments to functions in Python (*args, **kwargs) and their use cases.": "'*args' allows a function to accept a variable number of positional arguments. These arguments are collected into a tuple. '**kwargs' allows a function to accept a variable number of keyword arguments. These arguments are collected into a dictionary. They are useful when you don't know the exact number or names of arguments a function might receive.",
    "Explain the concept of closures in Python with an example.": "A closure is a function object that remembers values in enclosing scopes even if those scopes are no longer present in memory. This happens when a nested function refers to a variable from its enclosing function's scope. The inner function 'closes over' the variables from its environment.",
    "Elaborate on the use of decorators for logging, timing, and authentication. Provide examples.": "Decorators provide a clean way to add cross-cutting concerns like logging, timing, or authentication to functions without modifying their core logic. For example, a logging decorator can wrap a function to record when it's called and with what arguments. A timing decorator can measure the execution time. An authentication decorator can check if a user is authorized to execute the function.",
    "Discuss the implementation and benefits of generators and iterators in Python.": "Iterators are objects that allow traversal through a sequence of values one at a time using the '__next__()' method. Generators are a convenient way to create iterators using generator functions (with 'yield' statements) or generator expressions. They are memory-efficient for large sequences because they produce values on demand rather than storing the entire sequence in memory.",
    "Explain the different ways to handle file I/O in Python, including binary and text modes, and best practices for resource management.": "Python's 'open()' function allows you to interact with files in various modes ('r', 'w', 'a', 'b', 't', '+'). Text mode ('t') handles encoding and decoding of text data, while binary mode ('b') works with raw bytes. The 'with' statement is the recommended way to manage file resources as it automatically closes the file even if errors occur.",

    # --- Object-Oriented Programming (Advanced Concepts) ---
    "Explain the principles of SOLID in object-oriented design and how they relate to Python.": "SOLID is an acronym representing five principles of good object-oriented design: Single Responsibility Principle, Open/Closed Principle, Liskov Substitution Principle, Interface Segregation Principle, and Dependency Inversion Principle. While Python's dynamic nature allows for some flexibility, adhering to these principles can lead to more maintainable, scalable, and robust code.",
    "Discuss the use of abstract base classes (ABCs) and interfaces in Python for creating flexible and extensible designs.": "Abstract base classes (using the 'abc' module) define interfaces by requiring subclasses to implement specific methods. They cannot be instantiated directly. While Python doesn't have explicit 'interface' keywords like some other languages, ABCs serve a similar purpose in defining contracts and ensuring that related classes adhere to a common structure.",
    "Elaborate on the concept and implementation of metaclasses and their advanced use cases (e.g., enforcing coding standards, automatic registration).": "Metaclasses control the creation of classes. By defining a custom metaclass, you can intercept the class creation process, modify class attributes and methods, or enforce specific coding standards. Advanced use cases include automatically registering subclasses, implementing singletons, or creating domain-specific languages.",
    "Explain the nuances of method resolution order (MRO) in Python's multiple inheritance using the C3 linearization algorithm.": "When a class inherits from multiple base classes, the MRO defines the order in which base classes are searched for a method. Python uses the C3 linearization algorithm to ensure a consistent and predictable MRO, maintaining local precedence and monotonicity.",
    "Discuss the use of properties for controlled attribute access and validation in Python classes.": "Properties provide a way to implement getter, setter, and deleter methods for class attributes while allowing access using the standard attribute syntax. This enables you to add logic for validation, computation, or controlled access without breaking the interface of your class.",
    "Explain the implementation and benefits of operator overloading for creating more expressive and intuitive code with custom objects.": "Operator overloading allows you to define how standard operators behave with instances of your classes. For example, you can define the '+' operator to perform custom addition logic for your objects, making your code more readable and aligned with mathematical or domain-specific notations.",

    # --- Concurrency and Parallelism (In-Depth) ---
    "Compare and contrast threads and processes in Python, including their memory management and communication mechanisms.": "Threads are lightweight units of execution within a single process, sharing the same memory space. This makes communication between threads easier but also requires careful synchronization to avoid race conditions. Processes are independent units of execution with their own memory spaces, requiring explicit mechanisms (like pipes, queues, shared memory) for inter-process communication. Processes are generally better for CPU-bound tasks to bypass the GIL.",
    "Elaborate on the Global Interpreter Lock (GIL) in CPython and its implications for multithreading performance.": "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode at the same time within a single process. This limits the ability of multithreaded CPython programs to fully utilize multi-core processors for CPU-bound tasks.",
    "Discuss various techniques for achieving parallelism in Python to overcome the GIL limitations (multiprocessing, asynchronous programming).": "To achieve true parallelism in Python for CPU-bound tasks, the 'multiprocessing' module is used to create separate processes. For I/O-bound tasks, asynchronous programming with 'asyncio' allows efficient handling of concurrent operations by switching between tasks while waiting for I/O, often within a single thread.",
    "Explain the principles of asynchronous programming in Python using 'async' and 'await', and its benefits for I/O-bound operations.": "Asynchronous programming enables non-blocking I/O operations. 'async' defines a coroutine (a function that can be paused and resumed), and 'await' suspends the execution of a coroutine until an awaitable object (like a future or another coroutine) completes. This allows a single thread to handle many I/O-bound tasks concurrently without blocking.",
    "Discuss the use of thread pools and process pools for managing concurrent tasks efficiently.": "Thread pools (using 'concurrent.futures.ThreadPoolExecutor') and process pools (using 'concurrent.futures.ProcessPoolExecutor') provide a high-level interface for managing a pool of worker threads or processes. This allows you to submit tasks and have them executed concurrently, managing the overhead of thread/process creation and destruction.",
    "Explain different synchronization primitives in Python (locks, semaphores, events, conditions) and their use cases for managing shared resources in concurrent environments.": "Synchronization primitives are used to control access to shared resources in concurrent programs and prevent race conditions. Locks provide exclusive access to a resource. Semaphores manage a limited number of resources. Events signal that a certain condition has occurred. Conditions allow threads to wait until a specific condition is met.",

    # --- Networking and Web Development (Advanced) ---
    "Discuss the architecture and principles of RESTful APIs and how they are implemented in Python using frameworks like Flask and Django REST framework.": "RESTful APIs are designed based on Representational State Transfer principles, using standard HTTP methods (GET, POST, PUT, DELETE) to interact with resources identified by URLs. Frameworks like Flask and Django REST framework provide tools for defining routes, handling requests, serializing data (e.g., to JSON), and implementing API logic.",
    "Elaborate on different authentication and authorization mechanisms for web APIs in Python (e.g., Basic Auth, API Keys, JWT, OAuth 2.0).": "Web API security involves verifying the identity of the client (authentication) and determining what actions they are allowed to perform (authorization). Common mechanisms include Basic Auth (simple but insecure), API Keys (for identifying applications), JWT (JSON Web Tokens for stateless authentication), and OAuth 2.0 (for secure delegated authorization).",
    "Discuss the use of web sockets for real-time communication in Python web applications.": "Web sockets provide a persistent, bidirectional communication channel between a client and a server, enabling real-time interactions (e.g., chat applications, live updates). Libraries like 'websockets' and framework integrations in Flask and Django support web socket implementation.",
    "Explain the role of message queues (e.g., Celery, RabbitMQ, Kafka) for handling background tasks and improving scalability in Python web applications.": "Message queues decouple tasks from the main application flow, allowing them to be processed asynchronously by worker processes. This improves responsiveness and scalability by offloading long-running or resource-intensive tasks.",
    "Discuss advanced topics in network programming with Python's 'socket' module, including TCP/IP and UDP communication, and building custom network protocols.": "The 'socket' module provides low-level access to the network stack, allowing you to implement custom network protocols using TCP (reliable, connection-oriented) or UDP (unreliable, connectionless) communication. This is useful for specialized networking applications.",

    # --- Databases (Advanced) ---
    "Elaborate on advanced features of Object-Relational Mappers (ORMs) like SQLAlchemy (e.g., relationships, transactions, query optimization).": "ORMs like SQLAlchemy provide powerful features for interacting with relational databases in a Pythonic way, including defining complex relationships between tables, managing transactions for data integrity, and optimizing database queries for performance.",
    "Discuss different NoSQL database types (e.g., document, key-value, graph) and their use cases with Python drivers (e.g., PyMongo, Redis-py, Neo4j Python Driver).": "NoSQL databases offer different data models compared to relational databases. Document databases (like MongoDB) store JSON-like documents. Key-value stores (like Redis) store data as key-value pairs. Graph databases (like Neo4j) represent data as nodes and relationships. Python drivers provide APIs to interact with these databases.",
    "Explain database schema migrations and how they are managed in Python web frameworks (e.g., Alembic with SQLAlchemy, migrations in Django).": "Schema migrations are changes to the database structure. Web frameworks often provide tools to manage these changes in a controlled and versioned way, allowing you to evolve your database schema as your application evolves.",
    "Discuss techniques for database performance optimization in Python applications (e.g., indexing, query optimization, connection pooling).": "Optimizing database performance involves strategies like creating appropriate indexes, writing efficient SQL queries (or ORM queries), and using connection pooling to reuse database connections and reduce overhead.",

    # --- Specialized Python Topics ---
    "Explain the concepts and applications of metaprogramming in Python beyond metaclasses (e.g., dynamic code generation, attribute manipulation).": "Metaprogramming involves writing code that manipulates code. Beyond metaclasses, this includes techniques like dynamically creating classes or functions at runtime, modifying attributes of objects programmatically, and using tools like code generation libraries.",
    "Discuss the use of Python for scientific computing with libraries like NumPy, SciPy, and Pandas, including advanced array manipulation, numerical algorithms, and data analysis techniques.": "These libraries provide powerful tools for numerical computation (NumPy), scientific algorithms (SciPy), and data manipulation and analysis (Pandas), forming the foundation for many scientific and data science applications in Python.",
    "Elaborate on the application of Python in machine learning and deep learning with libraries like scikit-learn, TensorFlow, and PyTorch, covering model building, training, and evaluation.": "Python is a dominant language in machine learning and deep learning, with libraries providing tools for various tasks, from classical machine learning algorithms (scikit-learn) to building and training complex neural networks (TensorFlow, PyTorch).",
    "Discuss the use of Python for GUI development with libraries like Tkinter, PyQt, and Kivy, highlighting their strengths and weaknesses.": "Python offers several GUI libraries. Tkinter is a simple, built-in option. PyQt is a powerful and feature-rich cross-platform framework. Kivy is designed for modern, touch-based interfaces. Each has its own strengths and weaknesses in terms of complexity, features, and platform support.",
    "Explain the role of Python in web scraping and data extraction using libraries like Beautiful Soup and Scrapy.": "Python is widely used for web scraping (extracting data from websites). Beautiful Soup is a library for parsing HTML and XML. Scrapy is a more comprehensive framework for building web scraping spiders.",
    "Discuss the use of Python for network automation and infrastructure as code (IaC) with libraries like Netmiko, Ansible, and SaltStack.": "Python is increasingly used for automating network devices and managing infrastructure. Libraries like Netmiko simplify SSH connections to network devices. Tools like Ansible and SaltStack, often used with Python, enable infrastructure automation through code.",

    # --- SQL ---
    "What is SQL?": "SQL stands for Structured Query Language and is used to manage and query relational databases.",
    "What are SQL joins?": "Joins combine rows from two or more tables based on a related column. Types: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.",
    "What is a primary key in SQL?": "A primary key uniquely identifies each record in a table and cannot contain NULL values.",
    "What is a foreign key?": "A foreign key is a column that creates a relationship between two tables.",
    "What is the difference between WHERE and HAVING in SQL?": "'WHERE' filters rows before grouping, 'HAVING' filters groups after aggregation.",
    "What are aggregate functions in SQL?": "Aggregate functions operate on sets of values and return a single result. Examples: COUNT, SUM, AVG, MAX, MIN.",
    "What is a subquery in SQL?": "A subquery is a query nested inside another query. It can be used in SELECT, FROM, or WHERE clauses.",
    "What is normalization in SQL?": "Normalization is the process of organizing data to reduce redundancy and improve integrity.",
    "What is the difference between DELETE and TRUNCATE in SQL?": "'DELETE' removes rows based on a condition and can be rolled back. 'TRUNCATE' removes all rows and is faster, but can't be rolled back in most DBs.",
    "How do you handle NULL values in SQL?": "Use IS NULL or IS NOT NULL in conditions. Functions like COALESCE or IFNULL help replace NULL values.",
    "what_is_database": "A database is an organized collection of structured information, or data, typically stored electronically.",
    "what_is_table": "A table is a collection of related data with rows representing records and columns representing attributes.",
    "what_is_column": "A column defines a specific attribute or field within a table, holding data of a particular type.",
    "what_is_row": "A row (or record) represents a single instance or entry in a table.",
    "what_is_sql_query": "An SQL query is a request to retrieve, manipulate, or manage data in a database.",
    "what_is_select": "SELECT retrieves data from one or more tables.",
    "what_is_from": "FROM specifies the table(s) to query.",
    "what_is_where": "WHERE filters rows based on a condition.",
    "what_is_orderby": "ORDER BY sorts the result set.",
    "what_is_groupby": "GROUP BY groups rows with the same values.",
    "what_is_limit": "LIMIT restricts the number of rows returned.",
    "what_is_distinct": "DISTINCT returns only unique rows.",
    "comparison_operators": "=, !=, >, <, >=, <= for comparing values.",
    "logical_operators_sql": "AND, OR, NOT for combining conditions.",
    "like_operator": "LIKE for pattern matching with wildcards.",
    "wildcards": "% (any sequence), _ (single character) for pattern matching.",
    "in_operator": "IN checks if a value is in a list.",
    "between_operator": "BETWEEN checks if a value is within a range.",
    "alias": "AS provides a temporary name to tables or columns.",
    "inner_join": "INNER JOIN returns matching rows from both tables.",
    "left_join": "LEFT JOIN returns all from left, matching from right (NULL if no match).",
    "right_join": "RIGHT JOIN returns all from right, matching from left (NULL if no match).",
    "full_join": "FULL JOIN returns all rows with matches where available (NULL if no match).",
    "self_join": "Self-join joins a table to itself.",
    "cross_join": "CROSS JOIN returns the Cartesian product of rows.",
    "count_function": "COUNT() returns the number of rows.",
    "sum_function": "SUM() returns the sum of values.",
    "avg_function": "AVG() returns the average of values.",
    "max_function": "MAX() returns the maximum value.",
    "min_function": "MIN() returns the minimum value.",
    "having_clause": "HAVING filters groups after aggregation.",
    "subquery": "A subquery is a query nested within another.",
    "correlated_subquery": "A correlated subquery depends on the outer query.",
    "view": "A view is a virtual table based on a query result.",
    "index": "An index improves data retrieval speed.",
    "primary_key": "Uniquely identifies each record, cannot be NULL.",
    "foreign_key": "Links records between tables.",
    "unique_constraint": "Ensures all values in a column are distinct.",
    "not_null_constraint": "Ensures a column cannot have NULL values.",
    "check_constraint": "Limits the values allowed in a column.",
    "default_constraint": "Provides a default value for a column if none is specified.",
    "insert_statement": "INSERT INTO adds new rows.",
    "update_statement": "UPDATE modifies existing rows.",
    "delete_statement": "DELETE FROM removes rows based on a condition.",
    "truncate_statement": "TRUNCATE TABLE removes all rows quickly.",
    "alter_table": "ALTER TABLE modifies table structure.",
    "create_table": "CREATE TABLE defines a new table.",
    "drop_table": "DROP TABLE removes a table.",
    "normalization": "Organizing data to reduce redundancy.",
    "normalization_forms": "1NF, 2NF, 3NF, BCNF are normalization levels.",
    "transaction": "A sequence of operations as a single logical unit.",
    "acid_properties": "Atomicity, Consistency, Isolation, Durability of transactions.",
    "stored_procedure": "Pre-compiled SQL code stored in the database.",
    "trigger": "Code that automatically executes on database events.",
    "cursor": "Allows row-by-row processing of a result set.",
    "explicit_transaction": "Transactions started and ended explicitly (BEGIN TRANSACTION, COMMIT, ROLLBACK).",
    "implicit_transaction": "Each SQL statement treated as a single transaction.",
    "savepoint": "A point within a transaction to which you can roll back.",
    "locking": "Mechanisms to control concurrent access to data.",

    # --- SQL (More Advanced) ---
    "window_functions": "Perform calculations across a set of table rows related to the current row.",
    "partition_by": "Divides the result set into partitions for window functions.",
    "order_by_window": "Orders rows within a partition for window functions.",
    "row_number": "Assigns a unique sequential integer to each row within a partition.",
    "rank_function": "Assigns a rank to each row within a partition, with gaps for ties.",
    "dense_rank": "Assigns a rank without gaps for ties.",
    "lead_function": "Accesses data in a subsequent row within a partition.",
    "lag_function": "Accesses data in a preceding row within a partition.",
    "first_value": "Returns the first value in a partition.",
    "last_value": "Returns the last value in a partition.",
    "common_table_expression": "CTEs (WITH clause) are temporary, named result sets within a query.",
    "recursive_cte": "CTEs that can refer to themselves, useful for hierarchical data.",
    "pivot_table": "Transforms rows into columns.",
    "unpivot_table": "Transforms columns into rows.",
    "data_warehousing": "Centralized data storage for reporting and analysis.",
    "etl": "Extract, Transform, Load process for data warehousing.",
    "olap": "Online Analytical Processing for multidimensional data analysis.",
    "database_sharding": "Horizontal partitioning of data across multiple databases.",
    "database_replication": "Creating copies of a database for redundancy and availability.",
    "query_optimization": "Techniques to improve the performance of SQL queries.",
    "execution_plan": "Shows how the database executes a query.",
    "database_security": "Measures to protect database data and access.",
    "sql_injection": "A security vulnerability where malicious SQL statements are inserted.",
    "data_masking": "Obscuring sensitive data.",
    "data_encryption": "Encoding data to prevent unauthorized access.",
    "database_backup": "Creating copies of the database for recovery.",
    "database_restore": "Recovering a database from a backup.",
    "database_administration": "Tasks involved in managing and maintaining a database system.",
    "sql_dialects": "Variations of SQL syntax across different database systems (e.g., MySQL, PostgreSQL, SQL Server).",
    "stored_functions": "User-defined functions that can be used in SQL statements.",
    "database_triggers_advanced": "Complex trigger logic and use cases.",
    "spatial_data": "Handling geographical data in SQL.",
    "json_data_sql": "Working with JSON data within SQL databases.",
    "xml_data_sql": "Working with XML data within SQL databases.",
    "full_text_search": "Performing searches on textual data.",
    "performance_tuning": "Advanced techniques to optimize database performance.",
    "indexing_strategies": "Choosing the right types of indexes.",
    "query_hints": "Directives to the database optimizer.",
    "database_monitoring": "Tracking database performance and health.",
    "database_auditing": "Tracking database activity for security and compliance.",
    "data_modeling": "Designing the structure of a database.",
    "erd": "Entity-Relationship Diagram for data modeling.",
    "nosql_vs_sql": "Comparison of relational and non-relational databases.",
    "data_lake": "A centralized repository for storing vast amounts of raw data.",
    "data_governance": "Policies and procedures for managing data.",
    "data_lineage": "Tracking the origin and movement of data.",
    "temporal_tables": "Tables that store data history.",
    "common_sql_errors": "Understanding and troubleshooting common SQL errors.",
    "sql_standards": "ANSI SQL and other SQL standards.",
    "database_migration": "Moving data between different database systems.",
    "database_versioning": "Managing changes to the database schema.",
    "cloud_databases": "SQL databases offered as cloud services.",

    # --- EDA (Exploratory Data Analysis) ---
    "what_is_eda": "Exploratory Data Analysis (EDA) is an approach to analyzing datasets to summarize their main characteristics, often with visual methods.",
    "why_is_eda_important": "EDA helps in understanding the data's structure, identifying patterns, detecting outliers, and formulating hypotheses.",
    "what_are_the_goals_of_eda": "Goals include gaining insights, identifying variables, detecting anomalies, testing assumptions, and determining appropriate statistical models.",
    "what_are_common_eda_techniques": "Techniques include summary statistics, data visualization, and pattern identification.",
    "what_is_univariate_analysis": "Examining the distribution of a single variable.",
    "what_is_bivariate_analysis": "Examining the relationship between two variables.",
    "what_is_multivariate_analysis": "Examining the relationships among three or more variables.",

    # --- Data Loading and Initial Inspection ---
    "how_to_load_data_python_pandas": "Use pandas library with functions like `pd.read_csv()`, `pd.read_excel()`, etc.",
    "how_to_view_first_few_rows": "Use `dataframe.head()` in pandas.",
    "how_to_view_last_few_rows": "Use `dataframe.tail()` in pandas.",
    "how_to_get_data_summary": "Use `dataframe.info()` in pandas to get data types and non-null counts.",
    "how_to_get_descriptive_statistics": "Use `dataframe.describe()` in pandas for central tendency, dispersion, etc.",
    "how_to_check_data_types": "Access the `dataframe.dtypes` attribute in pandas.",
    "how_to_check_missing_values": "Use `dataframe.isnull().sum()` in pandas.",
    "how_to_check_duplicate_rows": "Use `dataframe.duplicated().sum()` in pandas.",
    "how_to_get_column_names": "Access the `dataframe.columns` attribute in pandas.",
    "how_to_get_number_of_rows_columns": "Use `dataframe.shape` in pandas.",

    # --- Univariate Analysis ---
    "eda_univariate_numerical_histogram": "Histograms visualize the distribution of a numerical variable.",
    "eda_univariate_numerical_boxplot": "Box plots show the summary statistics and potential outliers of a numerical variable.",
    "eda_univariate_numerical_kde": "Kernel Density Estimate plots smooth the distribution of a numerical variable.",
    "eda_univariate_numerical_violin_plot": "Combines aspects of box plots and KDE plots.",
    "eda_univariate_numerical_summary_statistics": "Mean, median, mode, standard deviation, quartiles, range.",
    "eda_univariate_categorical_countplot": "Count plots (bar charts) show the frequency of each category.",
    "eda_univariate_categorical_piechart": "Pie charts show the proportion of each category (use with caution).",
    "eda_univariate_categorical_value_counts": "Use `series.value_counts()` in pandas to get category frequencies.",
    "eda_univariate_categorical_percentage": "Calculate the percentage of each category.",

    # --- Bivariate Analysis ---
    "eda_bivariate_numerical_numerical_scatterplot": "Scatter plots show the relationship between two numerical variables.",
    "eda_bivariate_numerical_numerical_correlation": "Correlation coefficients (e.g., Pearson) quantify the linear relationship.",
    "eda_bivariate_numerical_numerical_jointplot": "Seaborn's `jointplot` shows scatter plot with univariate distributions.",
    "eda_bivariate_numerical_categorical_boxplot": "Box plots comparing a numerical variable across different categories.",
    "eda_bivariate_numerical_categorical_violinplot": "Violin plots comparing a numerical variable across different categories.",
    "eda_bivariate_numerical_categorical_stripplot": "Shows individual data points distributed along the categorical axis.",
    "eda_bivariate_numerical_categorical_swarmplot": "Similar to stripplot but adjusts points to avoid overlap.",
    "eda_bivariate_categorical_categorical_countplot_grouped": "Grouped bar charts show the frequency of categories for two variables.",
    "eda_bivariate_categorical_categorical_stacked_barplot": "Stacked bar charts show the proportion of categories for two variables.",
    "eda_bivariate_categorical_categorical_crosstab": "Contingency tables show the frequency of combinations of categories.",
    "eda_bivariate_categorical_categorical_chi2_test": "Chi-squared test can assess the independence of two categorical variables.",

    # --- Multivariate Analysis ---
    "eda_multivariate_scatterplot_matrix": "Pair plots show scatter plots for all pairs of numerical variables.",
    "eda_multivariate_correlation_matrix_heatmap": "Heatmaps visualize the correlation matrix of numerical variables.",
    "eda_multivariate_3d_scatterplot": "Scatter plots in three dimensions (if applicable).",
    "eda_multivariate_parallel_coordinates": "Visualizes multivariate data by plotting each observation as a line.",
    "eda_multivariate_ Andrews_curves": "Represents each multivariate observation as a periodic function.",
    "eda_multivariate_dimensionality_reduction_visualization": "Using PCA or t-SNE for visualizing high-dimensional data.",

    # --- Handling Missing Values ---
    "eda_missing_values_visualization_heatmap": "Heatmaps can show the pattern of missing values.",
    "eda_missing_values_visualization_missingno_library": "Libraries like `missingno` provide visualizations for missing data.",
    "eda_missing_values_imputation_mean_median_mode": "Basic imputation techniques for filling missing values.",
    "eda_missing_values_imputation_advanced": "Using more sophisticated methods like regression or KNN for imputation.",
    "eda_missing_values_deletion": "Removing rows or columns with missing values (use with caution).",

    # --- Outlier Detection and Handling ---
    "eda_outlier_detection_boxplot": "Box plots are useful for visually identifying outliers.",
    "eda_outlier_detection_z_score": "Identifying outliers based on standard deviations from the mean.",
    "eda_outlier_detection_iqr_method": "Using the Interquartile Range to define and detect outliers.",
    "eda_outlier_handling_removal": "Removing outlier data points (use with caution).",
    "eda_outlier_handling_transformation": "Transforming data to reduce the impact of outliers.",
    "eda_outlier_handling_imputation": "Replacing outliers with less extreme values.",
    "eda_outlier_handling_capping_flooring": "Limiting outlier values to a certain range.",

    # --- Data Transformation ---
    "eda_data_transformation_scaling": "Standardization or normalization to bring numerical variables to a similar scale.",
    "eda_data_transformation_log_transformation": "Useful for skewed data.",
    "eda_data_transformation_power_transformation": "A family of transformations to stabilize variance and reduce skewness.",
    "eda_data_transformation_encoding_categorical": "Converting categorical variables to numerical representations (e.g., one-hot encoding, label encoding).",

    # --- Time Series EDA (If Applicable) ---
    "eda_timeseries_line_plot": "Visualizing time series data over time.",
    "eda_timeseries_decomposition": "Separating time series into trend, seasonality, and residuals.",
    "eda_timeseries_autocorrelation_plot": "Examining the correlation of a time series with its past values.",
    "eda_timeseries_stationarity_check": "Assessing if the statistical properties of a time series remain constant over time.",

    # --- Reporting EDA Findings ---
    "eda_reporting_summaries": "Documenting key findings and insights from the analysis.",
    "eda_reporting_visualizations": "Presenting relevant charts and graphs.",
    "eda_reporting_conclusions_next_steps": "Outlining the implications of the EDA and suggesting further analysis.",
     # --- Data Science Fundamentals ---
    "what_is_data_science": "Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from noisy, structured, and unstructured data.",
    "what_is_machine_learning": "Machine Learning (ML) is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed.",
    "what_is_deep_learning": "Deep Learning (DL) is a subfield of ML that uses artificial neural networks with multiple layers to progressively extract higher-level features from the raw input.",
    "what_is_artificial_intelligence": "Artificial Intelligence (AI) is a broad field encompassing the theory and development of computer systems able to perform tasks that normally require human intelligence.",
    "what_is_supervised_learning": "ML where the algorithm learns from labeled data (input-output pairs).",
    "what_is_unsupervised_learning": "ML where the algorithm learns patterns from unlabeled data.",
    "what_is_reinforcement_learning": "ML where an agent learns to behave in an environment by performing actions and receiving rewards or punishments.",
    "what_is_model_evaluation": "Assessing the performance of a machine learning model using various metrics.",
    "what_is_feature_engineering": "Creating new features or transforming existing ones to improve model performance.",
    "what_is_model_deployment": "Making a trained machine learning model available for use in a real-world application.",

    # --- Machine Learning Algorithms (Supervised) ---
    "ml_linear_regression": "A linear model to predict a continuous output based on input features.",
    "ml_logistic_regression": "A linear model used for binary classification problems.",
    "ml_support_vector_machines": "SVMs find the optimal hyperplane to separate data points of different classes.",
    "ml_decision_trees": "Tree-like structures that make decisions based on feature values.",
    "ml_random_forest": "An ensemble method that builds multiple decision trees and averages their predictions.",
    "ml_gradient_boosting": "An ensemble method that builds trees sequentially, with each tree correcting the errors of the previous ones.",
    "ml_k_nearest_neighbors": "KNN classifies a data point based on the majority class of its k nearest neighbors.",
    "ml_naive_bayes": "A probabilistic classifier based on Bayes' theorem with the 'naive' assumption of feature independence.",

    # --- Machine Learning Algorithms (Unsupervised) ---
    "ml_k_means_clustering": "Partitions data into k clusters based on the distance to cluster centroids.",
    "ml_hierarchical_clustering": "Builds a hierarchy of clusters, either top-down (divisive) or bottom-up (agglomerative).",
    "ml_dbscan": "Density-Based Spatial Clustering of Applications with Noise; groups together points that are closely packed together.",
    "ml_principal_component_analysis": "PCA is a dimensionality reduction technique that finds the principal components of the data.",
    "ml_t_sne": "t-distributed Stochastic Neighbor Embedding; a dimensionality reduction technique for visualizing high-dimensional data.",
    "ml_association_rule_mining_apriori": "Discovers interesting relationships (associations) between variables in large datasets.",

    # --- Model Evaluation Metrics ---
    "evaluation_accuracy": "The fraction of predictions that the model got right.",
    "evaluation_precision": "Out of all positive predictions, what fraction were actually positive?",
    "evaluation_recall": "Out of all actual positives, what fraction did the model correctly identify?",
    "evaluation_f1_score": "The harmonic mean of precision and recall.",
    "evaluation_auc_roc": "Area Under the Receiver Operating Characteristic curve; measures the ability of a classifier to distinguish between classes.",
    "evaluation_mean_squared_error": "Average of the squared differences between the predicted and actual values (for regression).",
    "evaluation_r_squared": "Coefficient of determination; proportion of the variance in the dependent variable that is predictable from the independent variables (for regression).",
    "evaluation_confusion_matrix": "A table showing the counts of true positives, true negatives, false positives, and false negatives.",

    # --- Feature Engineering Techniques ---
    "feature_scaling_standardization": "Scaling features to have zero mean and unit variance.",
    "feature_scaling_normalization": "Scaling features to a specific range (e.g., 0 to 1).",
    "handling_categorical_one_hot_encoding": "Creating binary columns for each category.",
    "handling_categorical_label_encoding": "Assigning a unique numerical label to each category.",
    "handling_categorical_ordinal_encoding": "Assigning numerical labels based on the order of categories.",
    "handling_missing_data_imputation": "Filling in missing values using statistical measures or models.",
    "handling_missing_data_deletion": "Removing rows or columns with missing values.",
    "creating_polynomial_features": "Generating new features by raising existing features to certain powers or combining them.",
    "binning_numerical_features": "Grouping numerical values into discrete bins.",
    "feature_selection_techniques": "Methods to identify the most relevant features for a model.",

    # --- Deep Learning Basics ---
    "deep_learning_neural_networks": "Computational models inspired by the human brain, composed of interconnected nodes (neurons) in layers.",
    "deep_learning_activation_functions": "Introduce non-linearity to neural networks (e.g., ReLU, sigmoid, tanh).",
    "deep_learning_layers": "Organize neurons into input, hidden, and output layers.",
    "deep_learning_backpropagation": "Algorithm for training neural networks by adjusting weights based on the error.",
    "deep_learning_gradient_descent": "Optimization algorithm used to minimize the loss function.",
    "deep_learning_convolutional_neural_networks": "CNNs are effective for image and video processing.",
    "deep_learning_recurrent_neural_networks": "RNNs are designed for sequential data (e.g., text, time series).",
    "deep_learning_loss_functions": "Quantify the error between predicted and actual values.",
    "deep_learning_optimizers": "Algorithms to update the weights of a neural network (e.g., Adam, SGD).",
    "deep_learning_overfitting": "When a model learns the training data too well and performs poorly on unseen data.",
    "deep_learning_regularization": "Techniques to prevent overfitting (e.g., L1, L2 regularization, dropout).",

    # --- AI Ethics and Responsible AI ---
    "ai_ethics_bias": "Systematic and unfair prejudice in data or algorithms.",
    "ai_ethics_fairness": "Ensuring AI systems treat all groups equitably.",
    "ai_ethics_transparency": "Understanding how AI systems make decisions.",
    "ai_ethics_accountability": "Establishing responsibility for the outcomes of AI systems.",
    "ai_ethics_privacy": "Protecting sensitive data used in AI systems.",
    "responsible_ai_principles": "Guiding principles for the ethical development and deployment of AI.",

    # --- Natural Language Processing (NLP) Basics ---
    "nlp_tokenization": "Splitting text into individual words or units (tokens).",
    "nlp_stemming": "Reducing words to their root form.",
    "nlp_lemmatization": "Reducing words to their base or dictionary form (lemma).",
    "nlp_stop_words": "Common words often removed during text processing.",
    "nlp_tf_idf": "Term Frequency-Inverse Document Frequency; a numerical statistic that reflects the importance of a word in a document.",
    "nlp_word_embeddings": "Representing words as dense vectors in a continuous vector space (e.g., Word2Vec, GloVe).",

    # --- Computer Vision Basics ---
    "computer_vision_image_classification": "Assigning a label to an entire image.",
    "computer_vision_object_detection": "Identifying and localizing objects within an image.",
    "computer_vision_image_segmentation": "Dividing an image into meaningful regions.",
    "computer_vision_feature_extraction": "Identifying key features in an image (e.g., edges, corners).",

    # --- Model Deployment Basics ---
    "model_deployment_api": "Deploying a model as an API for other applications to use.",
    "model_deployment_cloud": "Deploying models on cloud platforms (e.g., AWS, Azure, GCP).",
    "model_deployment_edge": "Deploying models on local devices.",
    "model_monitoring": "Tracking the performance of a deployed model over time.",
    # --- Time Series Analysis (Advanced) ---
    "time_series_arima": "Autoregressive Integrated Moving Average; a statistical model for time series forecasting.",
    "time_series_prophet": "A forecasting procedure implemented in Python and R, developed by Facebook.",
    "time_series_lstm_for_forecasting": "Using Long Short-Term Memory networks (a type of RNN) for time series prediction.",
    "time_series_stationarity_tests_adf_kpss": "Augmented Dickey-Fuller and Kwiatkowski-Phillips-Schmidt-Shin tests to check for stationarity.",
    "time_series_seasonal_decomposition_stl": "Seasonal-Trend decomposition using Loess; a robust method for decomposing time series.",

    # --- Reinforcement Learning (More Detail) ---
    "rl_q_learning": "A model-free reinforcement learning algorithm to learn the value of an action in a particular state.",
    "rl_deep_q_networks": "Using deep neural networks to approximate the Q-value function.",
    "rl_policy_gradients": "Directly learning a policy that maps states to actions.",
    "rl_actor_critic_methods": "Combining policy-based and value-based methods.",
    "rl_exploration_vs_exploitation": "The trade-off between trying new actions and exploiting known good actions.",

    # --- Natural Language Processing (Advanced) ---
    "nlp_transformers_architecture": "Neural network architectures like BERT, GPT, and T5 that have revolutionized NLP.",
    "nlp_sentiment_analysis_advanced": "Using deep learning for nuanced sentiment detection.",
    "nlp_named_entity_recognition": "Identifying and classifying named entities in text.",
    "nlp_text_generation": "Using models to generate human-like text.",
    "nlp_machine_translation": "Translating text from one language to another.",
    "nlp_question_answering": "Building systems that can answer questions based on a given text.",
    "nlp_topic_modeling": "Identifying abstract topics that occur in a collection of documents.",

    # --- Computer Vision (Advanced) ---
    "cv_object_detection_yolo_ssd": "Real-time object detection frameworks.",
    "cv_semantic_segmentation_unet": "A popular architecture for pixel-wise image segmentation.",
    "cv_instance_segmentation_mask_rcnn": "Detecting and segmenting individual objects in an image.",
    "cv_image_generation_gans": "Generative Adversarial Networks for creating new images.",
    "cv_transfer_learning_pretrained_models": "Using models trained on large datasets for new tasks.",

    # --- Explainable AI (XAI) ---
    "xai_lime": "Local Interpretable Model-agnostic Explanations; explaining individual predictions of any classifier.",
    "xai_shap": "SHapley Additive exPlanations; a game-theoretic approach to explain the output of any machine learning model.",
    "xai_feature_importance": "Determining which features have the most influence on a model's predictions.",
    "xai_saliency_maps": "Visualizing the parts of an input (e.g., image) that are most important for a model's output.",

    # --- AI in Specific Domains ---
    "ai_healthcare": "Applications of AI in diagnosis, drug discovery, personalized medicine, etc.",
    "ai_finance": "Applications of AI in fraud detection, algorithmic trading, risk management, etc.",
    "ai_autonomous_vehicles": "AI for self-driving cars, including perception, planning, and control.",
    "ai_robotics": "Integrating AI with robots for tasks like navigation, manipulation, and human-robot interaction.",
    "ai_recommendation_systems": "Algorithms to suggest relevant items to users.",

    # --- MLOps (Machine Learning Operations) ---
    "mlops_cicd_for_ml": "Implementing continuous integration and continuous delivery for machine learning workflows.",
    "mlops_model_registry": "Managing and versioning trained models.",
    "mlops_model_monitoring_deployment": "Tracking model performance in production.",
    "mlops_feature_store": "A centralized repository for storing and managing features.",

    # --- Edge AI ---
    "edge_ai_deployment_on_devices": "Running AI models on resource-constrained devices.",
    "edge_ai_model_optimization_quantization": "Reducing the size and computational cost of models for edge deployment.",

    # --- Quantum Machine Learning (Emerging) ---
    "quantum_machine_learning_basics": "Exploring the intersection of quantum computing and machine learning.",
    "quantum_algorithms_for_ml": "Quantum algorithms that could potentially speed up machine learning tasks.",

    # --- Generative AI ---
    "generative_ai_models": "Models that can generate new data instances (e.g., images, text, audio).",
    "generative_ai_applications": "Use cases like content creation, data augmentation, and synthetic data generation.",

    # --- Causal Inference ---
    "causal_inference_basics": "Inferring cause-and-effect relationships from data.",
    "causal_inference_techniques": "Methods like instrumental variables, difference-in-differences, and propensity score matching.",
}


# --- Math Detection and Evaluation ---
def is_math_expression(text):
    pattern = re.compile(r"^[0-9+\-*/().\s^%e]+$")
    return bool(pattern.fullmatch(text.replace('^', '**')))

def evaluate_expression(expression):
    try:
        expression = expression.replace('^', '**')
        result = eval(expression, {"__builtins__": {}}, {
            "abs": abs,
            "round": round,
            "math": math,
            "sqrt": math.sqrt,
            "log": math.log,
            "exp": math.exp,
            "pow": pow,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e
        })
        return str(result)
    except ZeroDivisionError:
        return "Oops! You tried dividing by zero, which isn't allowed."
    except ValueError as ve:
        return f"Math error: {str(ve)}"
    except SyntaxError:
        return "Syntax error: Please check your expression."
    except Exception as e:
        return f"Sorry, I couldn't compute that. Error: {str(e)}"

# --- FAQ Chatbot Logic ---
def get_faq_answer(user_question):
    if is_math_expression(user_question):
        return evaluate_expression(user_question)
    best_match, score = process.extractOne(user_question.lower(), faq_data.keys())
    if score >= 70:
        return faq_data[best_match]
    return "Sorry, I couldn't find a good match for that question."

# --- Routes ---
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('message', '')
    answer = get_faq_answer(user_question)
    return jsonify({'response': answer})

@app.route('/send_feedback_mail', methods=['POST'])
def send_feedback():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    suggestion = data.get('suggestion')

    msg = EmailMessage()
    msg['Subject'] = f"Feedback from {name} (Age: {age})"
    msg['From'] = os.getenv("GMAIL_USER")
    msg['To'] = os.getenv("GMAIL_RECEIVER")
    msg.set_content(f"Name: {name}\nAge: {age}\n\nSuggestion:\n{suggestion}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
            smtp.send_message(msg)
        return jsonify({"message": "📬 Feedback sent successfully!"})
    except Exception as e:
        return jsonify({"message": f"❌ Failed to send feedback: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
