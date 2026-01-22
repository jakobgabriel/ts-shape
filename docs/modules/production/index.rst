Production Modules
==================

Complete suite of production tracking and analysis modules for daily manufacturing operations.

Overview
--------

The production module provides 5 essential tools for manufacturing:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Module
     - Description
   * - :doc:`part_tracking`
     - Track production quantities by part number
   * - :doc:`cycle_time_tracking`
     - Analyze cycle times and detect trends
   * - :doc:`shift_reporting`
     - Shift-based performance analysis and comparison
   * - :doc:`downtime_tracking`
     - Machine availability and downtime root cause analysis
   * - :doc:`quality_tracking`
     - NOK (defective parts) and quality metrics

Quick Example
-------------

.. code-block:: python

   from ts_shape.production import (
       PartProductionTracking,
       CycleTimeTracking,
       ShiftReporting,
       DowntimeTracking,
       QualityTracking,
   )

   # Production tracking
   prod = PartProductionTracking(df)
   daily = prod.daily_production_summary('part_id', 'counter')

   # Downtime analysis
   dt = DowntimeTracking(df)
   availability = dt.downtime_by_shift('state', running_value='Running')

   # Quality tracking
   qual = QualityTracking(df)
   nok = qual.nok_by_shift('ok_counter', 'nok_counter')

Design Principles
-----------------

All production modules follow these principles:

1. **One UUID Per Signal** - Each UUID represents exactly one signal
2. **Simple DataFrames** - All methods return pandas DataFrames
3. **Shift-Based** - Support shift analysis with custom definitions
4. **Daily Questions** - Answer practical plant manager questions
5. **No Over-Engineering** - Simple, focused implementations

Module Details
--------------

.. toctree::
   :maxdepth: 2

   part_tracking
   cycle_time_tracking
   shift_reporting
   downtime_tracking
   quality_tracking
