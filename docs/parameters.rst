.. _parameters:

Built-in Parameters
===================

The OpenPathSampling CLI comes with a number of parameters (i.e., options
and arguments) that can be passed to your commands. Be very shy about adding
new parameters; in general, it is best to re-use the parameters that already
exist. This is because re-using these parameters provides important
consistency in the user experience.

Here are the parameters that are pre-defined in the ``parameters.py`` file:

.. include:: parameter_table.rst

If you need a parameter that isn't in that list, it could either be:

* a one-off for just your command: just use ``click``.
* something to be reused: your should make an instance of a subclass of
  :class:`.AbstractLoader`, or duck-type something that behaves the same
  way. You need a method ``MYPARAMTER.clicked()`` that takes the an argument
  ``required`` and creates the ``click`` decorator, as well as a method
  ``get`` that extracts the correct form of the parameter you need.


