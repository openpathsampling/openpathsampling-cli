.. _interpretation:

Parameter Interpretation
========================

The core idea of the OpenPathSamping CLI is to identify things on the
command line that can be loaded from an existing OPS storage file. In the
simplest cases, objects were named, and therefore they can be looked up by
name. Data objects, such as snapshots, trajectories, and sample sets, cannot
be directly named. However, they can be stored in the ``tags`` store with
name, which gives essentially the same functionality.

But what if the user didn't name/tag the objects? Can we do anything then?

To an extent, yes. Here's how that the CLI interprets the command line
parameters for different types of objects.

.. note::

   We **strongly** recommend that users name or tag the objects that they
   will use with the CLI. It removes ambiguity and will make your life
   easier.  Everything else is just in case you forgot to do it the easy
   way!

Simulation objects with multiple instances
------------------------------------------

*Volumes, CVs, etc.*

Objects like volumes (typically as states) and CVs can often be specified
multiple times on the command line. These objects *must* named to be used.

Most OPS simulation objects can be named (before storing them) using
``obj.named("name")``, which returns the named object. We recommend doing
this on the same line where you define the object, e.g.:

.. code:: python

   state = paths.CVDefinedVolume(cv, min, max).named("state")

CVs are the exception to using ``.named()``: they currently require names on
initialization.

Single simulation objects
-------------------------

*Networks, move schemes, engines, etc.*

When searching for objects like networks, move schemes,
and engines, the CLI allows users to specify the name, the number of the
object in storage, or to expect the CLI to try to guess (if they specify
nothing).

If an value is given on the command line, the order of the checks is:

1. Take the value given on the command line, and check for an object of that
   name.
2. If there is no such object and the value can be converted to an integer,
   take the object with that integer value in storage. This uses Python
   notation, so we count from 0 and negative values are allowed, counting
   from the end of the list (so ``-1`` will return the last item in that
   store).

If no value is given on the command line, then the CLI tries to guess. It
goes through the following steps:

1. If there is only one object in the desired store, use that.
2. If only one object in the store has a name, use the named object.

If the CLI is unable to identify an appropriate object, it will raise an
error and exit.

Sample sets, trajectories, snapshots
------------------------------------

This starts with the same process as above, with the additional
understanding that initial conditions for path sampling can come from a
trajectory, from a list of trajectories, or from an existing sample set.

Sample sets, trajectories, and snapshots can not be named in the same way as
other objects, but the same effect can be achieved by tagging them. You can
tag an object in OPS with ``storage.tags['tag_name'] = obj``. If a value is
provided on the command line, the CLI looks for sample sets, trajectories,
and snapshots as follows:

1. Look in the tags for an object with the tag given on the command line.
2. If there is no such object and the value can be converted into an
   integer, take the object with that number in from the appropriate store.
   Again, this is counting from 0, and allows negatives (so, for example,
   the last sample set saved to a file can be accessed with ``-1``).
3. If the value cannot be converted into an integer, the CLI checks to see
   if it is the name of a file, and attempts to open that file. NOTE:
   although many file types are recognized and opened, most will not have
   velocities associated with them. OPS will assign all atoms zero velocity
   by default.

.. TODO add exception to get velocities from TRR files -- this should
   probably go into the core OPS library as part of the general
   load_trajectory function


In no command line parameter is provided, then it goes through the following
steps:

1. If there is only one object in the desired store, use that (for sample
   sets, this first tries the ``samplesets`` store, and then the
   ``trajectories`` store).
2. If more than one object is in the store, it checks the tags, first for an
   object labelled ``final_conditions`` (assuming you're continuing from a
   previous simulation), then for an object labelled ``initial_conditions``
   (if you have created a new setup file). Note that the OPS CLI tools use
   these tag names when running a simulation, which means that you can often
   omit specification of input data for follow-up simulations.
