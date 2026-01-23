# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- OEETracking module (planned)
- ChangeoverTracking module (planned)
- Performance loss tracking (planned)

## [1.0.0] - 2024-01-22

### Added
- **DowntimeTracking** module for machine availability and downtime analysis
  - `downtime_by_shift()` - Calculate downtime and availability per shift
  - `downtime_by_reason()` - Root cause analysis of downtime
  - `top_downtime_reasons()` - Pareto analysis (80/20 rule)
  - `availability_trend()` - Track availability over time

- **QualityTracking** module for NOK (defective parts) and quality metrics
  - `nok_by_shift()` - NOK parts and First Pass Yield per shift
  - `quality_by_part()` - Quality metrics by part number
  - `nok_by_reason()` - Defect type analysis
  - `daily_quality_summary()` - Daily quality rollup

- Comprehensive test coverage (39 tests, 100% passing)
  - 21 tests for production tracking modules
  - 18 tests for downtime and quality modules

- Complete documentation
  - DAILY_PRODUCTION_MODULES.md - Production, cycle time, shift modules
  - DOWNTIME_QUALITY_MODULES.md - Downtime and quality modules
  - PRODUCTION_MODULES_SUMMARY.md - Complete overview
  - FUTURE_PRODUCTION_FEATURES.md - Roadmap

- GitHub Actions workflow for automated documentation deployment
- Sphinx documentation with GitHub Pages support

### Changed
- Enhanced module imports in `__init__.py`
- Improved pandas merge handling to avoid column suffix issues
- Updated all shift-based modules to support custom shift definitions

### Fixed
- Column suffix issues in pandas merge_asof operations
- Empty reason filtering in quality tracking
- Timezone handling in shift assignment

## [0.9.0] - 2024-01-15

### Added
- **PartProductionTracking** module for production quantity tracking
  - `production_by_part()` - Production by time window and part
  - `daily_production_summary()` - Daily totals
  - `production_totals()` - Totals over date ranges

- **CycleTimeTracking** module for cycle time analysis
  - `cycle_time_by_part()` - Calculate cycle times
  - `cycle_time_statistics()` - Statistical analysis
  - `detect_slow_cycles()` - Anomaly detection
  - `cycle_time_trend()` - Trend analysis
  - `hourly_cycle_time_summary()` - Hourly summaries

- **ShiftReporting** module for shift-based analysis
  - `shift_production()` - Production per shift
  - `shift_comparison()` - Compare shift performance
  - `shift_targets()` - Target vs actual analysis
  - `best_and_worst_shifts()` - Performance ranking

- Test coverage for production tracking (21 tests)

### Design
- Established "one UUID per signal" design principle
- Simple DataFrame in/out interface
- Shift-based analysis with custom shift definitions
- Focus on practical daily questions

## [0.8.0] and Earlier

Previous versions focused on:
- Data loading modules (Azure, Parquet, S3)
- Event detection (production events, changeovers, machine states)
- Feature extraction (cycles, SPC, outliers)
- Filters and transformations
- Metadata management

---

## Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Types of Changes

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes

## Links

- [Unreleased](https://github.com/your-org/ts-shape/compare/v1.0.0...HEAD)
- [1.0.0](https://github.com/your-org/ts-shape/compare/v0.9.0...v1.0.0)
- [0.9.0](https://github.com/your-org/ts-shape/releases/tag/v0.9.0)
