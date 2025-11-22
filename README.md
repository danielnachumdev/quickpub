# QuickPub v3.0.61

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**QuickPub** is a **local CI/CD simulation tool** that brings the power of cloud-based continuous integration directly to your development environment. Instead of waiting for cloud CI/CD pipelines to catch issues, QuickPub runs all quality checks, tests, and validations locally - ensuring higher build pass rates and faster feedback loops.

## 🎯 **Why QuickPub?**

### **Local CI/CD Simulation**
- **Pre-Push Validation**: Run all CI/CD checks locally before pushing to remote repositories
- **Faster Feedback**: Catch issues immediately in your IDE without waiting for cloud builds
- **Customizable Error Display**: Format and display errors exactly how you want them
- **Higher Build Success Rate**: Ensure your code passes all checks before it reaches cloud pipelines
- **Cost Effective**: Reduce cloud CI/CD costs by catching issues locally first

### **Developer Experience**
- **IDE Integration**: Run comprehensive checks directly from your development environment
- **Real-time Validation**: Get instant feedback on code quality, tests, and package configuration
- **Consistent Environment**: Use the same validation logic locally and in production
- **Debugging Friendly**: Easier to debug and fix issues when they're caught locally

## 🚀 Features

### 🔧 **Build System**
- **Setuptools Integration**: Automated build process with `pyproject.toml` generation
- **Multiple Build Schemas**: Extensible build system supporting different packaging strategies
- **Automatic File Generation**: Creates `setup.py`, `pyproject.toml`, and `MANIFEST.in` files

### 🛡️ **Quality Assurance (Local CI/CD Simulation)**
- **Multi-Environment Testing**: Test across multiple Python versions and environments locally
- **Built-in QA Runners** (Same as cloud CI/CD):
  - **MyPy**: Static type checking with configurable error thresholds
  - **Pylint**: Code quality analysis with customizable scoring
  - **Pytest**: Comprehensive testing framework with coverage reporting
  - **Unittest**: Traditional unit testing with pass/fail metrics
- **Configurable Bounds**: Set minimum/maximum acceptable scores for each QA tool
- **Parallel Execution**: Run QA checks across multiple environments simultaneously
- **Local Environment Validation**: Ensure your code works across all target Python versions

### 🔒 **Constraint Enforcement**
- **Version Validation**: Ensure new versions are higher than existing ones
  - **Local Version Check**: Prevents overwriting existing local builds
  - **PyPI Remote Check**: Validates against published versions on PyPI
- **File Validation**: 
  - **README Enforcer**: Ensures README file exists and is valid
  - **License Enforcer**: Validates license file presence and format
  - **PyPI RC Enforcer**: Verifies PyPI configuration for uploads

### 🚀 **Deployment & Upload**
- **Multiple Upload Targets**:
  - **PyPI Upload**: Direct upload to Python Package Index
  - **GitHub Upload**: Automatic git commit and push with version tags
- **Configurable Credentials**: Secure credential management for different platforms

### 🐍 **Python Environment Management**
- **Multi-Environment Support**: Test across different Python versions locally
- **Conda Integration**: Full support for Conda environments
- **System Python**: Use system Python interpreter
- **Custom Executables**: Support for custom Python installations

### 📦 **Package Configuration**
- **Automatic Metadata**: Generate package metadata from project structure
- **Dependency Management**: Handle complex dependency specifications
- **Classifier Support**: Automatic PyPI classifier assignment
- **Keywords & Descriptions**: Comprehensive package documentation

## 📋 Requirements

- **Python**: 3.8.0 or higher
- **Tested Versions**: 3.8.0, 3.9.0, 3.10.13

## 🛠️ Installation

```bash
pip install quickpub
```

## 📖 Quick Start

### **Local CI/CD Workflow**

```python
from quickpub import publish, MypyRunner, PylintRunner, UnittestRunner, CondaPythonProvider, \
    PypircUploadTarget, SetuptoolsBuildSchema, GithubUploadTarget, PypircEnforcer, ReadmeEnforcer, LicenseEnforcer, \
    PypiRemoteVersionEnforcer, LocalVersionEnforcer

def main() -> None:
    # Run local CI/CD simulation - all checks happen locally before any cloud deployment
    publish(
        name="my-awesome-package",
        version="1.0.0",
        author="Your Name",
        author_email="your.email@example.com",
        description="A fantastic Python package",
        homepage="https://github.com/yourusername/my-awesome-package",
        
        # Local Quality Assurance (simulates cloud CI/CD)
        global_quality_assurance_runners=[
            MypyRunner(bound="<=20", configuration_path="./mypy.ini"),
            PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
            UnittestRunner(bound=">=0.95"),
        ],
        
        # Local Build & Upload (only if all checks pass)
        build_schemas=[SetuptoolsBuildSchema()],
        upload_targets=[PypircUploadTarget(), GithubUploadTarget()],
        
        # Local Environment Testing (multiple Python versions)
        python_interpreter_provider=CondaPythonProvider(["base", "39", "380"]),
        
        # Local Validation (prevents common CI/CD failures)
        enforcers=[
            PypircEnforcer(), 
            ReadmeEnforcer(), 
            LicenseEnforcer(),
            LocalVersionEnforcer(), 
            PypiRemoteVersionEnforcer()
        ],
        
        # Package Configuration
        dependencies=["requests>=2.25.0", "numpy>=1.20.0"],
        min_python="3.8.0",
        keywords=["automation", "publishing", "python"],
    )

if __name__ == '__main__':
    main()
```

## 🔧 Configuration Options

### Quality Assurance Runners (Local CI/CD Simulation)

#### MyPy Runner
```python
MypyRunner(
    bound="<=20",                    # Maximum number of errors allowed
    configuration_path="./mypy.ini", # Custom mypy configuration
    target="./src"                   # Target directory to check
)
```

#### Pylint Runner
```python
PylintRunner(
    bound=">=0.8",                   # Minimum score required (0-10 scale)
    configuration_path="./.pylintrc", # Custom pylint configuration
    target="./src"                   # Target directory to analyze
)
```

#### Pytest Runner
```python
PytestRunner(
    bound=">=0.9",                   # Minimum test pass rate
    target="./tests",                # Test directory
    no_tests_score=0.0               # Score when no tests are found
)
```

#### Unittest Runner
```python
UnittestRunner(
    bound=">=0.95",                  # Minimum test pass rate
    target="./tests",                # Test directory
    no_tests_score=0.0               # Score when no tests are found
)
```

### Python Environment Providers (Local Multi-Version Testing)

#### Conda Provider
```python
CondaPythonProvider(
    env_names=["base", "py39", "py38"],  # List of conda environments to test locally
    auto_install_dependencies=True,       # Auto-install required packages
    exit_on_fail=True                     # Exit on first failure
)
```

#### Default Provider
```python
DefaultPythonProvider()  # Uses system Python interpreter
```

### Upload Targets

#### PyPI Upload
```python
PypircUploadTarget(
    pypirc_file_path="./.pypirc",  # Path to PyPI configuration
    verbose=True                    # Enable verbose output
)
```

#### GitHub Upload
```python
GithubUploadTarget(
    verbose=True  # Enable verbose output
)
```

### Constraint Enforcers

#### Version Enforcers
```python
# Check against local builds
LocalVersionEnforcer()

# Check against PyPI published versions
PypiRemoteVersionEnforcer()
```

#### File Enforcers
```python
# Ensure README exists
ReadmeEnforcer(readme_file_path="./README.md")

# Ensure LICENSE exists
LicenseEnforcer(license_file_path="./LICENSE")

# Validate PyPI configuration
PypircEnforcer(pypirc_file_path="./.pypirc")
```

## 🏗️ Project Structure

QuickPub automatically generates the following files:

```
your-project/
├── pyproject.toml          # Package configuration
├── setup.py               # Setuptools configuration
├── MANIFEST.in            # Package manifest
├── your-package/          # Source code directory
│   └── __init__.py
├── tests/                 # Test directory
├── README.md              # Project documentation
├── LICENSE                # License file
└── .pypirc               # PyPI credentials (optional)
```

## 🔍 Advanced Features

### Custom Quality Assurance

You can create custom QA runners by extending the `QualityAssuranceRunner` class:

```python
from quickpub.strategies import QualityAssuranceRunner

class CustomQARunner(QualityAssuranceRunner):
    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        return f"custom-tool {target}"
    
    def _install_dependencies(self, base: LayeredCommand) -> None:
        with base:
            base("pip install custom-tool")
    
    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        # Custom score calculation logic
        return 0.95
```

### Progress Tracking (Customizable Error Display)

```python
from tqdm import tqdm
import json

def main() -> None:
    publish(
        # ... other parameters ...
        log=lambda obj: tqdm.write(json.dumps(obj, default=str)),  # Custom error formatting
        pbar=tqdm(desc="Local CI/CD Progress", leave=False),       # Custom progress display
    )
```

### Demo Mode (Local CI/CD Testing)

Test your configuration without making changes:

```python
publish(
    # ... other parameters ...
    demo=True,  # Run all local CI/CD checks without building or uploading
)
```

## 🐛 Troubleshooting

### Common Issues

1. **QA Failures**: Check your bound configurations and ensure your code meets the quality thresholds
2. **Version Conflicts**: Use `PypiRemoteVersionEnforcer` to avoid version conflicts
3. **Environment Issues**: Verify your Python environments are properly configured
4. **Upload Failures**: Ensure your PyPI credentials are correctly configured in `.pypirc`

### Debug Mode

Enable verbose output for detailed logging:

```python
publish(
    # ... other parameters ...
    log=print,  # Print all log messages with custom formatting
)
```

## 🚀 **Local CI/CD Benefits**

### **Before QuickPub (Traditional Workflow)**
1. Write code
2. Push to repository
3. Wait for cloud CI/CD to run
4. Fix issues if build fails
5. Repeat steps 2-4 until success

### **With QuickPub (Local CI/CD)**
1. Write code
2. Run QuickPub locally (simulates entire CI/CD pipeline)
3. Fix issues immediately with better error visibility
4. Push to repository with confidence
5. Cloud CI/CD passes on first try! ✅

### **Key Advantages**
- **Faster Development**: No waiting for cloud builds
- **Better Error Visibility**: Customize how errors are displayed
- **Cost Savings**: Reduce cloud CI/CD usage
- **Higher Success Rate**: Catch issues before they reach production
- **IDE Integration**: Run checks directly from your development environment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the Python community
- Inspired by the need for streamlined package publishing workflows
- Thanks to all contributors and users who have helped improve QuickPub

---

**QuickPub** - Your local CI/CD companion for Python package publishing! 🚀