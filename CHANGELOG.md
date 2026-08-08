# Changelog

All notable changes to QuickPub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.1.2] - 2026-08-08

### Added
- `UvBuildSchema` — build with `uv build` from `pyproject.toml`
- `publish(generate_project_files=False)` — keep existing packaging files; bump `[project].version` only

### Changed
- `PypircUploadTarget` finds sdists by package name or PEP 503 normalized name (hyphen vs underscore)
- Removed unused `SetuptoolsBuildSchema(backend=...)` argument

## [3.0.1] - 2025-06-28

### 🚀 **Major Enhancements**
- **Enhanced README.md**: Completely rewritten to showcase QuickPub as a local CI/CD simulation tool
- **Fixed PyPI Remote Version Enforcer**: Improved HTML parsing logic to correctly handle PyPI simple package index format

### 🔧 **Technical Improvements**
- Updated PyPI version enforcer to use proper regex parsing for anchor tags
- Enhanced test coverage for remote version checking
- Improved error handling and validation logic

## [3.0.0] - 2025-03-25

### 🚀 **Major Features**
- **AsyncWorkerPool Integration**: Implemented concurrent QA step execution for improved performance
- **Progress Bar Support**: Added optional progress bar functionality for better user experience
- **Enhanced Logging**: Added optional log function for QA step and future step logging

### 🔧 **Technical Improvements**
- **Better Error Messaging**: More informative error messages for sanity checks
- **CondaPythonProvider Enhancement**: Now raises ExitEarlyError if requested environment is not available
- **Improved Test Structure**: Better test classes and more efficient job structure
- **Concurrent Processing**: All QA steps now run concurrently for faster execution

### 🐛 **Bug Fixes**
- Fixed issue where tests didn't finish properly
- Resolved problems with unittest runner handling multiple instances
- Fixed test setup issues across different environments

## [2.0.4] - 2024-08-28

### 🚀 **New Features**
- **CLI Support**: Added command-line interface functionality
- **Performance Improvements**: Made tests run 2x faster
- **Alternative Version Support**: Added support for alternative versioning schemes

### 🔧 **Technical Improvements**
- Enhanced test performance and execution speed
- Improved CLI integration and user experience

## [2.0.3] - 2024-08-28

### 🔧 **Technical Improvements**
- Performance optimizations and test improvements
- Enhanced CLI functionality

## [2.0.2] - 2024-08-05

### 🔧 **Technical Improvements**
- Fixed default provider compatibility with updated danielutils
- Enhanced test coverage and reliability
- Improved dependency management

### 🐛 **Bug Fixes**
- Fixed compatibility issues with danielutils updates
- Resolved test failures across different environments

## [2.0.1] - 2024-08-05

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [2.0.0] - 2024-08-05

### 🚀 **Major Features**
- **Enhanced Test Structure**: Complete test restructuring for better organization
- **Improved Test Coverage**: Added comprehensive tests for all components
- **Better Documentation**: Enhanced docstrings and documentation

### 🔧 **Technical Improvements**
- Restructured test files for better maintainability
- Added more test files and improved test organization
- Enhanced IDE configuration support
- Fixed Python 3.8.0 compatibility issues

### 🐛 **Bug Fixes**
- Fixed compatibility issues with Python 3.8.0
- Resolved test failures across different environments

## [1.0.3] - 2024-07-15

### 🚀 **Major Features**
- **Strategy-Based Architecture**: Transformed enforcers to use strategy pattern
- **Enhanced Test Coverage**: Added comprehensive tests for enforcers
- **Remote Version Enforcer**: Added PyPI remote version checking capability

### 🔧 **Technical Improvements**
- Moved all strategies into correct folder structure
- Added AutoCWDTestCase for better test management
- Implemented TestLocalVersionEnforcer
- Added testing for SetuptoolsBuildSchema
- Enhanced file organization and structure

### 🐛 **Bug Fixes**
- Fixed imports and file structure issues
- Resolved test failures after structural changes

## [1.0.2] - 2024-07-14

### 🚀 **Major Features**
- **Strategy Pattern Implementation**: Implemented build, upload, and commit as strategies
- **Pytest Integration**: Added pytest_qa_runner.py for comprehensive testing
- **Enhanced File Organization**: Moved files to correct locations

### 🔧 **Technical Improvements**
- Renamed files, classes, and parameters for better clarity
- Updated README.md with current information
- Enhanced docstring documentation
- Improved code structure and organization

### 🐛 **Bug Fixes**
- Fixed publish.py functionality
- Resolved test failures after structural changes

## [1.0.1] - 2024-07-13

### 🚀 **Major Features**
- **Dependency Management**: Added Dependency class for better dependency handling
- **Version Checking**: Implemented dependency version checking functionality
- **Enhanced Package Structure**: Renamed inner packages for better organization

### 🔧 **Technical Improvements**
- Updated docstrings and documentation
- Enhanced error message formatting
- Improved code structure and readability

### 🐛 **Bug Fixes**
- Fixed compatibility issues with danielutils updates
- Resolved error message formatting issues

## [1.0.0] - 2024-07-13

### 🚀 **Major Features**
- **Quality Assurance System**: Complete QA system with multiple runners
- **Visual Feedback**: Progress bars and better user feedback
- **Enhanced Error Handling**: Better formatted and informative error messages
- **Sanity Checks**: Re-introduced comprehensive sanity checking

### 🔧 **Technical Improvements**
- **CondaPythonManager**: Better support for Conda environment management
- **QA Check Structure**: Improved QA check organization and execution
- **Error Message Formatting**: Enhanced error message formatting in base runner
- **Pool Management**: Better pool printing and management

### 🐛 **Bug Fixes**
- Fixed crash with pylint runner
- Resolved wrongful exit conditions
- Fixed mypy and pylint integration issues
- Enhanced error message formatting

## [0.8.31] - 2024-04-28

### 🚀 **Major Features**
- **Progress Bar Integration**: Good MVP for visual feedback using ProgressBars
- **Enhanced User Experience**: Better visual feedback during operations

## [0.8.3] - 2024-04-28

### 🔧 **Technical Improvements**
- Updated List and Tuple imports for better compatibility
- Enhanced code structure and organization

## [0.8.2] - 2024-04-28

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.8.1] - 2024-04-28

### 🔧 **Technical Improvements**
- Updated runnables to remove redundant code
- Enhanced code efficiency and maintainability

## [0.8.0] - 2024-04-28

### 🚀 **Major Features**
- **Unittest Integration**: Implemented unittest tester for comprehensive testing
- **Quality Assurance**: MVP for implementing pylint and unittest into package
- **Enhanced Testing**: Better handling of tests and analysis

### 🔧 **Technical Improvements**
- Lowered minimum Python version requirements
- Tests working on Python 3.9.0
- Enhanced test handling and execution
- Improved code structure and organization

## [0.7.0] - 2024-04-22

### 🔧 **Technical Improvements**
- Code cleanup and optimization
- Enhanced test handling and execution
- Better code organization and structure

## [0.6.34] - 2024-03-30

### 🚀 **New Features**
- **Test Integration**: Added comprehensive test suite
- **Enhanced Testing**: Better test coverage and execution

### 🔧 **Technical Improvements**
- Added test for main function
- Enhanced test infrastructure

## [0.6.32] - 2024-03-29

### 🔧 **Technical Improvements**
- Added comprehensive docstring documentation
- Enhanced code documentation and readability

## [0.6.31] - 2024-03-29

### 🚀 **New Features**
- **Explicit Path Definitions**: Added explicit readme and license path definitions
- **Enhanced Configuration**: Better configuration management

## [0.6.30] - 2024-03-29

### 🔧 **Technical Improvements**
- **Better Upload Error Handling**: Enhanced error handling for upload operations
- **Source Validation**: Added validator for source directory with warnings
- **Enhanced Error Messages**: More informative error messages

## [0.6.1] - 2024-03-29

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.6.0] - 2024-03-29

### 🔧 **Technical Improvements**
- Enhanced code structure and organization

## [0.5.5] - 2024-03-29

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.5.2] - 2024-03-22

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.5.1] - 2024-03-22

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.5.0] - 2024-03-22

### 🔧 **Technical Improvements**
- Minor version update and bug fixes

## [0.0.1] - 2024-03-22

### 🚀 **Initial Release**
- **Core Functionality**: Basic package publishing capabilities
- **Initial Structure**: Foundation for the QuickPub package
- **Basic Features**: Essential publishing and build functionality

## [Unreleased] - 2024-03-21

### 🚀 **Project Initialization**
- **Initial Commit**: Project foundation and basic structure
- **Core Architecture**: Established the basic architecture for QuickPub

---

## Legend

- 🚀 **Major Features**: New significant features and capabilities
- 🔧 **Technical Improvements**: Code improvements, optimizations, and enhancements
- 🐛 **Bug Fixes**: Bug fixes and issue resolutions
- 📚 **Documentation**: Documentation updates and improvements
- 🔒 **Security**: Security-related changes and improvements 