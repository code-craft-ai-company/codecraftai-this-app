# AutoMojo This-App Package Design Document

## Overview

The **automojo-this-app** package is a foundational Python library that provides application presence and configuration management for the Automation Mojo framework. It establishes a lightweight, extensible configuration system that allows applications to define their identity, manage settings with precedence rules, and maintain a persistent presence on the host machine.

## Architecture

### Core Components

#### 1. Application Identity (`ThisApplication`)
The central singleton class that represents the application's presence and manages its configuration lifecycle.

**Key Responsibilities:**
- Application identity management (name, logger, service configuration)
- Configuration file discovery and parsing
- Environment variable management with precedence rules
- Context-based object storage and retrieval
- Variable resolution and caching

**Configuration Precedence (highest to lowest):**
1. Application-level overrides
2. Environment variables
3. Settings file values
4. Default values

#### 2. Context System (`Context`, `ContextCursor`)
A hierarchical path-based storage system for application data and configuration.

**Features:**
- Path-style syntax (`/level1/level2/item`) for data organization
- Template filling capabilities using stored data
- Cursor-based navigation for nested data structures
- Support for both string paths and list-based paths

#### 3. Variable Management System

##### Variable Descriptors (`AppVarDesc`)
Declarative variable definitions that specify comprehensive constraints and behavior for application variables:

**Variable Constraints:**
- **Source Restrictions**: `VariableSource` flags control which sources can provide values (ENVIRONMENT, SETTINGS, BOTH, or NONE)
- **Section Mapping**: Configuration file section where the variable should be located
- **Default Values**: Fallback values when no source provides a value
- **Required Flag**: Indicates whether the variable must have a value or can be optional
- **Type Conversion**: Optional converter functions for transforming string values to appropriate Python types
- **Context Integration**: Optional context paths for automatic storage in the application context
- **Override Behavior**: Controls whether variable changes should update OS environment variables

**Constraint Enforcement:**
Variable descriptors act as both specification and enforcement mechanism, ensuring that variable access follows defined rules and precedence. The descriptor validates variable names against environment variable naming conventions and section names against INI file format requirements.

##### Variable Sets (`AppVarSet`)
Base class for grouping related variable descriptors using class-based declaration patterns.

##### Variable Accessors (`AppVarAccessor`)
Descriptor-based access to application variables with automatic resolution through the `ThisApplication` singleton.

**Access Pattern:**
Variable accessors implement the descriptor protocol to provide transparent, read-only access to application variables. When a variable is accessed through an accessor, it automatically resolves the value through the `ThisApplication` singleton using the associated variable descriptor.

**Read-Only Enforcement:**
Accessors prevent direct assignment to variables by raising `AttributeError` in the `__set__` method. This enforces controlled variable modification through the application's `override_variable_value()` method, maintaining clear audit trails for variable changes.

#### 4. Application Persona (`establish_app_persona`)
Initialization system that establishes the application's identity and presence settings.

**Configured Elements:**
- Application name and logging configuration
- Presence directory structure
- Settings file location
- Extension module loading
- Service identification

**Initialization Pattern:**
Applications must call `establish_app_persona()` early in their startup process, before any access to the `ThisApplication` singleton. This function configures the minimum variables needed for the application to operate with proper logging, presence directory management, and configuration file handling.

**Basic Initialization Example:**
```python
from automojo.thisapp.persona import establish_app_persona

# Minimal required configuration
establish_app_persona(
    name="testtool",                      # Short name for presence directory
    logger_name="TESTTOOL",               # Logger name (appears in log entries)
    log_basename="mytesttool"             # Base name for log files
)
```

**Full Configuration Example:**
```python
from automojo.thisapp.persona import establish_app_persona

# Complete configuration with all options
establish_app_persona(
    name="automtool",                                  # Required: Short name for presence directory
    logger_name="AUTOMTOOL",                           # Required: Logger name (appears in logs)
    log_basename="automation-tool",                    # Required: Log file base name
    presence_dir="/opt/automtool",                     # Optional: Custom presence directory
    log_directory="/var/log/automtool",                # Optional: Custom log directory
    settings_file="config/tool-settings.ini",         # Optional: Custom settings file
    extensions="myext.module1;myext.module2",         # Optional: Extension modules
    service_name="my-automation-service"               # Optional: Service identifier
)
```

**Default Behavior:**
When optional parameters are not provided, the system applies intelligent defaults:
- `presence_dir`: Defaults to `~/name.lower()` (e.g., `~/automtool`)
- `log_directory`: Defaults to `presence_dir/logs`
- `settings_file`: Defaults to `presence_dir/settings.config`
- `extensions`: Defaults to `None` (no extensions loaded)
- `service_name`: Defaults to `None`

**Configuration Impact:**
The persona establishment configures core application variables that enable:
- **Logging System**: Logger name and log file location for application logging
- **Presence Management**: Directory structure for configuration, data, and log storage
- **Configuration Loading**: Settings file location for INI-format configuration
- **Extension System**: Module loading for extensible functionality
- **Service Integration**: Service identification for system-level integration

**Application Entry Point Examples:**

*Command-Line Tool Entry Function:*
```python
#!/usr/bin/env python3

import sys
from automojo.thisapp.persona import establish_app_persona
from automojo.thisapp.wellknown import ThisApplicationSingleton

def main():
    """Main entry point for the test automation tool."""
    
    # Establish application persona FIRST - before any other initialization
    establish_app_persona(
        name="testrunner",
        logger_name="TESTRUNNER", 
        log_basename="test-runner",
        presence_dir="~/.testrunner",
        settings_file="testrunner.config"
    )
    
    # Now safe to access application singleton and other components
    this_app = ThisApplicationSingleton()
    
    # Continue with application logic...
    run_tests()

if __name__ == "__main__":
    main()
```

*Service/Daemon Entry Function:*
```python
#!/usr/bin/env python3

import logging
from automojo.thisapp.persona import establish_app_persona
from automojo.thisapp.wellknown import ThisApplicationSingleton

class AutomationService:
    
    def __init__(self):
        # Establish service persona at initialization
        establish_app_persona(
            name="automsvc",
            logger_name="AUTOMSVC",
            log_basename="automation-service",
            presence_dir="/opt/automsvc",
            log_directory="/var/log/automsvc", 
            settings_file="/etc/automsvc/service.config",
            extensions="automation.plugins.core;automation.plugins.extended",
            service_name="automation-service-daemon"
        )
        
        # Application persona is now established - safe to use singletons
        self.app = ThisApplicationSingleton()
        self.logger = logging.getLogger(self.app.logger_name)
        
    def start_service(self):
        """Start the automation service daemon."""
        self.logger.info("Starting automation service...")
        # Service implementation continues...

def main():
    """Service entry point."""
    service = AutomationService()
    service.start_service()

if __name__ == "__main__":
    main()
```

**Critical Timing:**
The `establish_app_persona()` call must occur before any attempt to access `ThisApplicationSingleton()` or any components that depend on the application configuration. This ensures the application has a properly defined identity and configuration foundation before any other initialization occurs.

### Data Flow

```
Application Startup
    ↓
establish_app_persona()
    ↓
ThisApplication Singleton Creation
    ↓
Variable Resolution (Environment → Settings → Defaults)
    ↓
Context Population
    ↓
Extension Loading
```

## Key Design Patterns

### 1. Singleton Pattern
- `ThisApplication` uses a thread-safe singleton pattern
- Enforced initialization through `establish_app_persona`
- Global access through `wellknown.ThisApplicationSingleton()`

### 2. Descriptor Pattern
- `AppVarAccessor` implements the descriptor protocol
- Provides transparent access to application variables
- Prevents direct assignment to maintain control flow

### 3. Declarative Configuration
- Class-based variable declaration using `AppVarDesc`
- Automatic name binding through `__set_name__`
- Inheritance-aware variable collection

### 4. Path-Based Storage
- Hierarchical context system with Unix-like paths
- Automatic intermediate node creation
- Type-aware cursor objects for nested navigation

### 5. Variable Access Control Pattern
**Read-Only Access Through Descriptors:**
Variables are accessed through `AppVarAccessor` descriptors that provide read-only access to resolved values. The accessor uses the associated `AppVarDesc` to retrieve values through the `ThisApplication` singleton, ensuring consistent resolution logic and caching.

**Controlled Modification Through Application Instance:**
Variable modifications must go through the `ThisApplication.override_variable_value()` method, which accepts:
- **Variable Descriptor**: The `AppVarDesc` that identifies the variable and carries its constraints
- **New Value**: The value to assign, which respects the descriptor's type and validation rules
- **Automatic Constraint Application**: The method automatically applies the descriptor's constraints (environment variable updates, context storage, override behavior)

**Constraint-Driven Resolution:**
The variable descriptor serves as both identifier and constraint specification during resolution. When `get_variable_value()` is called with an `AppVarDesc`, the method:
- Applies source restrictions (only checking allowed sources)
- Uses the descriptor's default value if no source provides a value
- Applies type conversion if a converter is specified
- Enforces required/optional behavior
- Stores the result in the designated context path if specified

This pattern ensures that variable access is always governed by the constraints defined in the descriptor, providing consistent behavior across all access points.

## Configuration Management

### Variable Sources
Variables can be sourced from multiple locations with configurable precedence:

- **Environment Variables**: OS-level environment variables
- **Settings Files**: INI-format configuration files
- **Application Defaults**: Hardcoded fallback values
- **Runtime Overrides**: Programmatic value assignment

### Variable Access and Modification Patterns

**Read Access Pattern:**
```python
class MyVariables:
    MY_VAR = AppVarAccessor(AppVarDesc(section="MAIN", default="default_value"))

# Read-only access through class attribute (no instance needed)
value = MyVariables.MY_VAR  # Automatically resolves through ThisApplication
```

**Modification Pattern:**
```python
# Variable modification must go through ThisApplication
this_app = ThisApplicationSingleton()
var_desc = MyVariablesDesc.MY_VAR  # The AppVarDesc instance

# Override with constraint enforcement
this_app.override_variable_value(var_desc, "new_value")
```

**Constraint Application During Access:**
When variables are accessed or modified, the `AppVarDesc` provides all necessary constraints:
- Source restrictions determine which resolution sources are consulted
- Default values are applied when no source provides a value
- Type converters transform string values to appropriate Python types
- Context paths enable automatic storage in the application context
- Override behavior controls environment variable synchronization
- Required flags enforce mandatory variable presence

**Descriptor-Driven Resolution:**
The `get_variable_value()` method uses the descriptor to apply all constraints during resolution:
```python
def get_variable_value(self, variable_desc: AppVarDesc, default=..., converter=None):
    # Uses variable_desc.source to determine valid sources
    # Applies variable_desc.default if no value found
    # Uses variable_desc.converter for type transformation
    # Stores in variable_desc.context_path if specified
```

### Settings File Format
Standard INI format with section-based organization:
```ini
[DEFAULT]
VARIABLE_NAME=value

[SECTION_NAME]
ANOTHER_VAR=another_value
```

### Context Paths
Well-known context paths for common application data (defined in `ContextPaths`):
- Environment information (`/environment/*`)
- Configuration data (`/configuration/*`)
- Job and pipeline metadata
- Logging and output directories

## Extension System

### Module Loading
- Semicolon-separated extension module specification
- Lazy loading through `ConfiguredSuperFactorySingleton`
- Integration with the SuperFactory pattern for extensible functionality

### Extension Configuration
Extensions are specified via the `AM_EXTENSIONS` variable and loaded on-demand when the SuperFactory is accessed.

## Error Handling

### Validation
- Variable name validation (environment variable compatible)
- Section name validation (INI file compatible)
- Path validation for context operations

### Exception Types
- `SemanticError`: Improper usage patterns (e.g., direct instantiation)
- `LookupError`: Context path resolution failures
- `KeyError`: Required variable not found
- `ValueError`: Invalid path or parameter formats

## Thread Safety

### Synchronization
- Thread-safe singleton initialization using `threading.RLock`
- Atomic variable resolution and caching
- Safe concurrent access to context data

### Concurrency Considerations
- Multiple threads can safely access resolved variables
- Context modifications should be coordinated at the application level
- Extension loading is thread-safe through singleton pattern

## Testing Strategy

### Unit Test Coverage
- Individual component isolation testing
- Mock-based dependency injection for external systems
- Comprehensive variable precedence validation
- Context path manipulation verification
- Error condition testing

### Test Patterns
- Setup/teardown for environment isolation
- Temporary directory usage for file-based tests
- Stub module installation for dependency management

## Performance Characteristics

### Optimization Features
- Variable value caching after first resolution
- Lazy loading of extension modules
- Efficient path parsing and validation
- Minimal memory footprint for context storage

### Scalability Considerations
- O(1) variable access after initial resolution
- Hierarchical context structure supports deep nesting
- Extension system allows modular functionality loading

## Security Considerations

### Access Control
- Controlled variable override mechanisms
- Validation of configuration file paths
- Environment variable sanitization

### Data Protection
- No sensitive data logging in variable resolution
- Secure handling of configuration file permissions
- Isolation of application presence directories

## Future Extensibility

### Extension Points
- Custom variable converters for type transformation
- Pluggable configuration sources beyond environment/files
- Context storage backends for distributed scenarios
- Custom validation rules for variable values

### Backward Compatibility
- Stable API surface for core functionality
- Versioned configuration file formats
- Graceful degradation for missing extensions