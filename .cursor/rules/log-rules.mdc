---
alwaysApply: true
---

# Logging Rules and Guidelines

## Overview

This document defines comprehensive rules for logging in the danielutils codebase. These rules ensure that logs provide valuable information to end users while avoiding log spam and maintaining good performance.

## Log Levels and When to Use Them

### DEBUG (Level 0)
**Purpose**: Detailed diagnostic information for development and debugging.

**When to use**:
- Method entry/exit points for complex operations
- Variable values during algorithm execution
- Detailed flow control information
- Internal state changes that are not visible to users
- Performance measurements and timing information

**Examples**:
```python
logger.debug("RetryExecutor initialized with backoff strategy: %s", type(backoff_strategy).__name__)
logger.debug("Converting graph with %d nodes to dictionary", len(self.nodes))
logger.debug("Attempt %d/%d", i + 1, max_retries)
```

**When NOT to use**:
- In tight loops that execute frequently
- For information that's always the same
- For obvious operations that don't add value

### INFO (Level 1)
**Purpose**: General information about program execution that would be useful to end users.

**When to use**:
- Successful completion of significant operations
- Important state changes that affect user experience
- Configuration changes
- User-initiated actions
- System status updates

**Examples**:
```python
logger.info("Starting retry execution with max_retries=%d", max_retries)
logger.info("Execution succeeded on attempt %d", i + 1)
logger.info("Task %d '%s' started on worker %s", task_index, name, worker_id)
```

**When NOT to use**:
- For routine operations that always succeed
- For internal implementation details
- For operations that happen very frequently

### WARNING (Level 2)
**Purpose**: Indicates something unexpected happened, but the program can continue.

**When to use**:
- Recoverable errors or fallback behaviors
- Deprecated feature usage
- Performance issues that don't break functionality
- Configuration problems that have defaults
- Resource exhaustion warnings

**Examples**:
```python
logger.warning("Attempt %d failed with %s: %s", i + 1, type(e).__name__, e)
logger.warning("RetryExecutor context exited with exception: %s: %s", exc_type.__name__, exc_val)
logger.warning("Using default configuration due to invalid user settings")
```

**When NOT to use**:
- For expected error conditions that are handled gracefully
- For user errors that are part of normal operation

### ERROR (Level 3)
**Purpose**: Serious problems that prevent a specific operation from completing.

**When to use**:
- Operations that fail and cannot be recovered
- Critical resource failures
- Data corruption or loss
- Security violations
- Unhandled exceptions in user-facing operations

**Examples**:
```python
logger.error("Task %d '%s' failed on worker %s: %s", task_index, name, worker_id, e)
logger.error("Failed to initialize database connection")
logger.error("Critical data validation failed")
```

**When NOT to use**:
- For expected failures that are part of normal flow
- For user input validation errors

### CRITICAL (Level 4)
**Purpose**: Very serious errors that may cause the program to stop running.

**When to use**:
- System-level failures
- Memory exhaustion
- Fatal configuration errors
- Security breaches
- Data loss that cannot be recovered

**Examples**:
```python
logger.critical("System memory exhausted, shutting down")
logger.critical("Database connection lost, cannot continue")
logger.critical("Security violation detected, terminating session")
```

## Logging Contexts and When to Log

### 1. Initialization and Configuration
- **Always log**: Component initialization with key parameters
- **Always log**: Configuration changes that affect behavior
- **Never log**: Default value assignments unless significant

### 2. User Operations
- **Always log**: User-initiated actions that have side effects
- **Always log**: Operations that take significant time (>1 second)
- **Always log**: Operations that modify persistent state
- **Never log**: Simple getter operations
- **Never log**: UI rendering operations

### 3. Error Handling
- **Always log**: All caught exceptions with context
- **Always log**: Fallback behaviors and recovery actions
- **Always log**: Resource allocation failures
- **Never log**: Expected exceptions that are part of normal flow

### 4. Performance and Resource Management
- **Always log**: Resource allocation and deallocation
- **Always log**: Performance metrics for long-running operations
- **Always log**: Memory usage warnings
- **Never log**: Every iteration of tight loops
- **Never log**: Routine resource checks

### 5. State Changes
- **Always log**: Significant state transitions
- **Always log**: Data structure modifications that affect behavior
- **Always log**: Connection state changes
- **Never log**: Temporary state changes
- **Never log**: Internal flag toggles

## Log Message Formatting Standards

### Message Structure
```
[Context] Action: Details (Additional Info)
```

### Examples
```python
# Good - using lazy evaluation
logger.info("Database connection established: %s:%d", host, port)
logger.warning("Retry attempt %d/%d failed: %s", attempt, max_retries, error)
logger.error("Failed to save user data: %s - %s", user_id, error)

# Bad - f-strings evaluate immediately
logger.info(f"Database connection established: {host}:{port}")
logger.warning(f"Retry attempt {attempt}/{max_retries} failed: {error}")
logger.error(f"Failed to save user data: {user_id} - {error}")

# Also bad - too generic
logger.info("Database connected")
logger.warning("Retry failed")
logger.error("Save failed")
```

### Variable Naming in Logs
- Use descriptive variable names in log messages
- Include relevant context (IDs, counts, types)
- Use consistent formatting for similar information

### Exception Logging
```python
# Good - using lazy evaluation
try:
    result = risky_operation()
except SpecificException as e:
    logger.error("Operation failed with %s: %s", type(e).__name__, e)
    raise
except Exception as e:
    logger.error("Unexpected error in operation: %s: %s", type(e).__name__, e)
    raise

# Bad - f-strings evaluate immediately
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

## Performance Considerations

### 1. Lazy Evaluation (CRITICAL)
**ALWAYS use lazy evaluation for expensive operations in log messages.** This is the most important performance consideration.

#### Use % formatting instead of f-strings for expensive operations:
```python
# Good - lazy evaluation with % formatting
logger.debug("Processing %d items", len(items))
logger.debug("Complex calculation result: %s", expensive_calculation())
logger.info("User %s performed action %s in %dms", user_id, action, duration)

# Bad - f-strings evaluate immediately
logger.debug(f"Processing {len(items)} items")
logger.debug(f"Complex calculation result: {expensive_calculation()}")
logger.info(f"User {user_id} performed action {action} in {duration}ms")
```

#### When to use f-strings vs % formatting:
```python
# Good - f-strings for simple, fast operations
logger.debug(f"RetryExecutor initialized with backoff strategy: {type(backoff_strategy).__name__}")
logger.info(f"Starting retry execution with max_retries={max_retries}")

# Good - % formatting for expensive operations
logger.debug("Database query result: %s", complex_database_query())
logger.info("File processing completed: %d files processed in %dms", file_count, processing_time)
logger.warning("Retry attempt %d/%d failed: %s", attempt, max_retries, str(exception))
```

#### Multiple arguments with lazy evaluation:
```python
# Good - all arguments evaluated lazily
logger.info("User %s uploaded file %s (size: %d bytes) in %dms", 
           user_id, filename, file_size, upload_time)

# Bad - f-string evaluates everything immediately
logger.info(f"User {user_id} uploaded file {filename} (size: {file_size} bytes) in {upload_time}ms")
```

### 2. Conditional Logging
Check log level before expensive operations:

```python
# Good
if logger.isEnabledFor(logging.DEBUG):
    debug_info = expensive_debug_calculation()
    logger.debug("Debug info: %s", debug_info)

# Bad
debug_info = expensive_debug_calculation()
logger.debug(f"Debug info: {debug_info}")
```

### 3. Avoid Logging in Tight Loops
```python
# Good - using lazy evaluation and periodic logging
logger.debug("Starting batch processing of %d items", len(items))
for i, item in enumerate(items):
    process_item(item)
    if i % 100 == 0:  # Log every 100 items
        logger.debug("Processed %d/%d items", i, len(items))
logger.debug("Batch processing completed")

# Bad - f-strings in tight loop
for item in items:
    logger.debug(f"Processing item: {item}")
    process_item(item)
```

## Logger Setup and Usage

### When to Add Logging to a File
**Only add logging to files that benefit from it.** Not every file needs logging. Consider adding logging when:

- **File has complex operations** that users need to monitor
- **File handles user interactions** or external system communications
- **File manages resources** (connections, workers, processes)
- **File performs long-running operations** that users wait for
- **File handles errors** that need to be tracked and debugged
- **File implements business logic** with multiple execution paths

**Do NOT add logging to files that are:**
- **Simple data containers** (pure data classes, enums, constants)
- **Pure utility functions** with no side effects
- **Simple getters/setters** without complex logic
- **Type definitions** or protocol definitions
- **Configuration files** or simple constants
- **Files with only imports and exports**

### Logger Initialization
Use Python's builtin logging module. Create loggers at module level:

```python
import logging

logger = logging.getLogger(__name__)
```

**Important**: Only import `logging` and create a `logger` if the file actually needs logging. If a file doesn't benefit from logging, don't add these imports.

### Strategy Pattern Logger Setup
When using the strategy design pattern, set up logging in the `__init_subclass__` method:

```python
import logging

class BaseStrategy:
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Use the module name for the logger to maintain proper hierarchy
        cls.logger = logging.getLogger(cls.__module__)
        cls.logger.debug(f"Strategy subclass '{cls.__name__}' initialized")
    
    def execute(self):
        self.logger.info(f"Executing strategy: {self.__class__.__name__}")
        # Strategy implementation here
```

### Logger Configuration
Configure loggers with appropriate levels and handlers:

```python
# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or configure specific logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

### Metadata Usage
Include relevant metadata in log messages using lazy evaluation:

```python
# Good - using lazy evaluation
logger.info("User action completed: user_id=%s, action=%s, file_size=%d, duration=%dms", 
           user.id, "file_upload", file.size, elapsed_time)

# Also acceptable for simple cases
logger.info("User action completed: user_id=%s, action=file_upload, file_size=%d, duration=%dms", 
           user.id, file.size, elapsed_time)
```

## Anti-Patterns to Avoid

### 1. Log Spam
```python
# Bad - logs every iteration with f-strings
for item in large_list:
    logger.debug(f"Processing item: {item}")

# Good - logs progress periodically with lazy evaluation
for i, item in enumerate(large_list):
    process_item(item)
    if i % 1000 == 0:
        logger.debug("Processed %d/%d items", i, len(large_list))
```

### 2. Redundant Logging
```python
# Bad - redundant information
logger.info("Starting operation")
logger.info("Operation in progress")
logger.info("Operation completed")

# Good - meaningful state changes with lazy evaluation
logger.info("Starting batch processing of %d items", item_count)
logger.info("Batch processing completed successfully")
```

### 3. Logging Sensitive Information
```python
# Bad - f-strings with sensitive data
logger.info(f"User login: {username}, password: {password}")

# Good - lazy evaluation without sensitive data
logger.info("User login attempt: %s", username)
logger.info("User authentication successful")
```

### 4. Inconsistent Log Levels
```python
# Bad - inconsistent use of levels
logger.debug("User logged in")  # Should be INFO
logger.info("Debug: processing item")  # Should be DEBUG
logger.warning("Operation completed successfully")  # Should be INFO
```

### 5. F-strings vs % Formatting Guidelines
**Use f-strings ONLY for simple, fast operations:**
```python
# Good - f-strings for simple operations
logger.debug(f"RetryExecutor initialized with backoff strategy: {type(backoff_strategy).__name__}")
logger.info(f"Starting retry execution with max_retries={max_retries}")
logger.warning("Using default configuration due to invalid user settings")  # No variables

# Bad - f-strings for expensive operations
logger.debug(f"Complex calculation result: {expensive_calculation()}")
logger.info(f"Database query result: {complex_database_query()}")
logger.warning(f"File processing completed: {file_count} files processed in {processing_time}ms")
```

**Use % formatting for expensive operations:**
```python
# Good - % formatting for expensive operations
logger.debug("Complex calculation result: %s", expensive_calculation())
logger.info("Database query result: %s", complex_database_query())
logger.warning("File processing completed: %d files processed in %dms", file_count, processing_time)
logger.error("Task %d '%s' failed on worker %s: %s", task_index, name, worker_id, e)
```

**Rule of thumb**: If the operation inside the braces `{}` could be expensive (function calls, complex calculations, string operations), use % formatting instead of f-strings.

## Testing and Validation

### 1. Log Level Testing
Test that appropriate log levels are used:
```python
def test_log_levels():
    with LogCapture() as logs:
        # Test that INFO level logs are generated
        operation()
        assert logs.records[0].levelname == "INFO"
```

### 2. Log Content Testing
Test that log messages contain expected information:
```python
def test_log_content():
    with LogCapture() as logs:
        retry_operation()
        assert "Retry attempt" in logs.records[0].message
        assert "failed" in logs.records[0].message
```

## Summary

These rules ensure that:
1. **Logs are informative**: They provide valuable context for debugging and monitoring
2. **Logs are not spammy**: They avoid unnecessary noise and performance impact
3. **Logs are consistent**: They follow predictable patterns and formatting
4. **Logs are useful to end users**: They provide information that helps users understand what's happening
5. **Logs are performant**: They don't impact application performance significantly through lazy evaluation
6. **Logs are selective**: Only files that benefit from logging should have logging imports and logger instances

**CRITICAL PERFORMANCE RULE**: 
- **ALWAYS use % formatting instead of f-strings for expensive operations in log messages**
- **Use f-strings ONLY for simple, fast operations like variable access or simple string formatting**

Remember: 
- **When in doubt, log at INFO level with meaningful context. It's better to have slightly more logging than to miss important information.**
- **Don't add logging imports to files that don't need them. Not every file benefits from logging.**
- **Performance matters: Lazy evaluation prevents expensive operations from running when logging is disabled.**
