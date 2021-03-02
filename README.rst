JadePix3 Software
=================

.. image:: https://readthedocs.org/projects/jadepix3-software/badge/?version=latest
    :target: https://jadepix3-software.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

This is the software for Jadepix3 verification. The software is designed based on `IPbus uHAL <https://ipbus.web.cern.ch/>`_.
The functions implemented:

- Configure the DAC70004 on the FMC(HPC) daughter PCB.
- Configure the JadePix3 via SPI.
- Configure each pixel in the JadePix3.
- Rolling shutter setup.
- Global shutter setup.
- Data acquisition.
- Data analysis by the ROOT.


Install the required libraries
------------------------------

.. note:: Please use **Python3.7** or higer!
.. code-block:: shell

    pip3 install -r requirements.txt
    pip3 install -e .

Run
---

1. Setup environment for IPbus uHAL
    .. code-block:: shell

        . setEnv.sh

2. Execute main script
    .. code-block:: shell

        ./run.py

You may want to plot data later individually
    .. code-block:: shell

        python3 data_analysis/data_analysis.py

.. note::
    1. SPI configuration
        The location of configuration file: *lib/jadepix_defs.py*. Consider to change the style be more general, eg, *\*.ini*, *\*.json*

    2. JadePix configuration
        The location of configuration file: *config/jadepix_config.txt*

Documentation
-------------

.. code-block:: shell

    sphinx-build -b html doc/source doc/build
    cd doc && make html

License
-------

The project is licensed under the GPLv3 license.