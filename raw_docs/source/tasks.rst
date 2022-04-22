.. _tasks:

=================
Tasks Overview
=================

There are a lot of tasks defined in the package. All of these methods are available in ``alab_experiment_helper.tasks``.
You can use them like this

.. code-block:: python

  from alab_experiment_helper.tasks import *
  from alab_experiment_helper import Experiment

  ...
  experiment = Experiment(name="test")
  samples = [experiment.add_sample(name="sample1"), experiment.add_sample(name="sample2")]

  heating(samples, **task_params)
  # more operations goes here


Here is the brief introduction to each tasks.

Dispensing
----------
Dispensing refers to the process done by Labman robot. It is the first step of the experiment. A ``.csv`` file is
required as the input file for Labman system.

.. autofunction:: alab_experiment_helper.tasks.dispensing.dispensing
  :noindex:

Heating
--------
Heating refers to the operation to put the sample into the box furnace and heat it to certain temperature.
For convenience, there is a ``simple_heating`` to make the tasks easier.

.. autofunction:: alab_experiment_helper.tasks.heating.simple_heating
  :noindex:

Also, there is a ``heating`` function to submit more complex heating tasks.

.. autofunction:: alab_experiment_helper.tasks.heating.heating
  :noindex:

Heating with Atmosphere
-----------------------

This operation will send samples to the tube furnace and heat them with certain atmosphere. Apart from the
atmosphere and flow rate, this operation has same parameter as ``heating``.

.. autofunction:: alab_experiment_helper.tasks.heating_with_atmosphere.heating_with_atmosphere
  :noindex:

Scraping
--------

Scraping is the operation to remove the sample powders out of the crucible after annealing. Since it will
use a ball milling method, user need to specify the shaking time and the number of milling balls for shaking.

.. autofunction:: alab_experiment_helper.tasks.scraping.scraping
  :noindex:

XRD
---

Do XRD on the sample.

.. autofunction:: alab_experiment_helper.tasks.xrd.xrd
  :noindex:

Disposing
---------

Dispose the samples to the right position (later human will decide to waste or store the samples).

.. autofunction:: alab_experiment_helper.tasks.disposing.disposing
  :noindex: