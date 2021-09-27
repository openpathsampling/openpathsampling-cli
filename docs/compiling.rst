
Compiling
=========

Let's start with an overview of terminology.:

* **Compiling**: The process of converting input in a text format,
  such as YAML or JSON, into OPS objects. Here we're focused on non-Python
  alternatives to using the standard Python interpreter to compile objects.
* **Category**: The base category of object to be created (engine, CV,
  volume, etc.)
* **Builder**: We will refer to a builder function, which creates an
  instance of a specific 

Everything is created with plugins. There are two types of plugins used in
the ``compiling`` subpackage:

* ``InstanceCompilerPlugin``: This is what you'll normally work with. These
  convert the input text to an instance of a specific OPS object (for
  example, an ``OpenMMEngine`` or an ``MDTrajFunctionCV``. In general, you
  do not create subclasses of ``InstanceCompilerPlugin`` -- there are
  subclasses specialized to engines (``EngineCompilerPlugin``), to CVs
  (``CVCompilerPlugin``), etc. You create *instances* of those subclasses.
  You write your builder function, and wrap in with in an instance of an
  ``InstanceCompilerPlugin``.
* ``CategoryPlugin``: These manage the plugins associated with a given
  features.  Contributors will almost never need to create one of these.
  The only case in which you would need to create one of these is if you're
  creating a new *category* of object, i.e., something like an engine where
  users will have multiple options at the command line.

Other useful classes defined in the ``compiling`` subpackage include:

* ``Builder``: The ``Builder`` class is a convenience for creating builder
  functions. It takes either a callable or a string as input, where a string
  is treated as a path to an object to import at runtime. It also allows
  takes parameters ``remapper`` and ``after_build``, which are callables
  that act on the input dictionary before object creation (``remapper``) and
  on the created object after object creations (``after_build``).
* ``CategoryCompiler``: This class manages plugins for a given category, as
  well as tracking named objects of that type. These are created
  automatically when plugins are registered; users do not need to create
  these.
