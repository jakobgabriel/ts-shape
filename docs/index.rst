ts-shape Documentation
======================

**ts-shape** is a comprehensive Python library for timeseries data analysis in manufacturing environments.

Simple, practical tools for everyday manufacturing needs following the **one UUID per signal** design principle.

.. image:: https://img.shields.io/badge/python-3.8%2B-blue
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green
   :alt: License

Quick Start
-----------

.. code-block:: python

   from ts_shape.production import (
       PartProductionTracking,
       CycleTimeTracking,
       ShiftReporting,
       DowntimeTracking,
       QualityTracking,
   )

   # Track production by part
   tracker = PartProductionTracking(df)
   daily_prod = tracker.daily_production_summary('part_id_uuid', 'counter_uuid')

   # Analyze downtime
   downtime = DowntimeTracking(df)
   shift_downtime = downtime.downtime_by_shift('state_uuid', running_value='Running')

   # Track quality
   quality = QualityTracking(df)
   nok_by_shift = quality.nok_by_shift('ok_counter_uuid', 'nok_counter_uuid')


Key Features
------------

**5 Essential Production Modules**

1. **PartProductionTracking** - Track production quantities by part number
2. **CycleTimeTracking** - Analyze cycle times and detect trends
3. **ShiftReporting** - Shift-based performance analysis
4. **DowntimeTracking** - Machine availability and downtime analysis
5. **QualityTracking** - NOK (defective parts) and quality metrics

**Manufacturing KPIs Supported**

* **Availability** - Uptime vs downtime analysis
* **Performance** - Cycle time tracking and optimization
* **Quality** - First Pass Yield and NOK rate tracking
* **OEE** - Overall Equipment Effectiveness (components)


Production Modules Overview
----------------------------

All modules answer critical daily questions that plant managers ask:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Module
     - Purpose
     - Key Questions
   * - PartProductionTracking
     - Production quantity tracking
     - How many parts did we make?
   * - CycleTimeTracking
     - Cycle time analysis
     - How fast are we producing?
   * - ShiftReporting
     - Shift-based summaries
     - How did each shift perform?
   * - DowntimeTracking
     - Availability & downtime
     - How much uptime did we have?
   * - QualityTracking
     - NOK parts & defects
     - What's our quality rate?


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/installation
   user_guide/quick_start
   user_guide/daily_production
   user_guide/downtime_quality
   user_guide/complete_guide

.. toctree::
   :maxdepth: 2
   :caption: Module Documentation

   modules/production/index
   modules/events/index
   modules/features/index
   modules/filters/index
   modules/data_loading/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/production
   api/events
   api/features
   api/filters
   api/data_loading

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   resources/future_features
   resources/contributing
   resources/changelog


Examples
--------

**Daily Production Dashboard**

.. code-block:: python

   # Complete daily performance picture
   from ts_shape.production import *

   # Quantity
   production = PartProductionTracking(df)
   daily_prod = production.daily_production_summary('part_id', 'counter')

   # Speed
   cycles = CycleTimeTracking(df)
   cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')

   # Availability
   downtime = DowntimeTracking(df)
   availability = downtime.downtime_by_shift('state', running_value='Running')

   # Quality
   quality = QualityTracking(df)
   quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')

   # Calculate simplified OEE
   avg_avail = availability['availability_pct'].mean()
   avg_fpy = quality_metrics['first_pass_yield_pct'].mean()
   oee = (avg_avail * avg_fpy) / 100
   print(f"OEE: {oee:.1f}%")


**Root Cause Analysis**

.. code-block:: python

   # Why did we have low production?

   # 1. Check downtime
   downtime = DowntimeTracking(df)
   shift_dt = downtime.downtime_by_shift('state', running_value='Running')

   # 2. Find top reasons
   top_reasons = downtime.top_downtime_reasons('state', 'reason', top_n=5)

   # 3. Check quality issues
   quality = QualityTracking(df)
   defects = quality.nok_by_reason('nok_counter', 'defect_reason')


Design Principles
-----------------

**1. One UUID Per Signal**

Each UUID represents exactly one signal - simple and clear.

**2. Simple DataFrame Returns**

All methods return pandas DataFrames - no complex objects.

**3. Shift-Based Analysis**

Most modules support shift analysis (default 3-shift or custom).

**4. Practical Daily Questions**

Every method answers a real question plant managers ask daily.

**5. No Over-Engineering**

Simple implementations focused on getting the job done.


Performance Benchmarks
-----------------------

All modules are optimized for performance:

* Production tracking: Process 1M records in <1 second
* Cycle time analysis: 10-50x faster with IntervalIndex optimization
* Downtime calculations: Real-time processing of shift data
* Quality metrics: Efficient aggregation for large datasets


Installation
------------

.. code-block:: bash

   pip install ts-shape


Support
-------

* **Documentation**: https://your-org.github.io/ts-shape
* **Issues**: https://github.com/your-org/ts-shape/issues
* **Source**: https://github.com/your-org/ts-shape


License
-------

This project is licensed under the MIT License.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
