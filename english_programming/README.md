# English Programming: Human Language Virtual Machine

> Program in plain English, no syntax required.

English Programming is a revolutionary system that allows you to write programs in plain English rather than conventional programming syntax. This is the unified implementation that combines all the best features from various development phases into a powerful, scalable architecture based on compilation and virtual machine execution.

## Core Features

- **Natural Language Syntax**: Write code as if you were explaining it to a person
- **Compiler/VM Architecture**: Programs are compiled to bytecode and executed by a virtual machine
- **Variable Operations**: Create and manipulate variables
- **Control Structures**: If/else conditions, while loops, and for-each loops
- **Functions**: Define functions with parameters and return values
- **File Operations**: Read from and write to files
- **API Integration**: Call external APIs like weather services
- **Multiple Interfaces**: Command-line and web interfaces

## Getting Started

### Running an English Program

```bash
# Compile and run a program
python english_programming.py examples/basic_operations.nl

# Or use the interactive launcher
python english_programming.py
```

### Example Programs

Several example programs are included in the `examples/` directory:

- `basic_operations.nl`: Demonstrates variables, printing, and loops
- `api_integration.nl`: Shows how to call external APIs

## Language Guide

### Creating Variables

```
Create a variable called name and set it to John
Create a variable called age and set it to 30
Create a variable called is_active and set it to true
```

### Basic Operations

```
Add x and y and store the result in sum
```

### Control Structures

```
If age is greater than 18:
    Print You are an adult
```

```
While count is less than 5:
    Add 1 to count
    Print count
```

### Functions

```
Define a function called greet with inputs name:
    Create a variable called message and set it to Hello
    Add message and name and store the result in full_message
    Print full_message
    Return full_message

Call greet with values John and store result in greeting
```

### File Operations

```
Read file data.txt and store lines in content
Write Hello World to file output.txt
```

### API Integration

```
Call OpenWeather API with city as London and store temperature in temp
Print temp
```

## System Architecture

The English Programming system is built on a two-stage execution model:

1. **Compilation Stage**: The natural language compiler (`enhanced_nl_compiler.py`) translates English code into bytecode instructions.

2. **Execution Stage**: The virtual machine (`enhanced_nlvm.py`) executes the bytecode to produce results.

This design mirrors how traditional programming languages work (like Java's JVM or Python's interpreter), providing a solid foundation for future enhancements and optimizations.

## Project Structure

```
english_programming/
├── src/
│   ├── compiler/        # English to bytecode compiler
│   ├── vm/              # Virtual machine for bytecode execution
│   ├── interfaces/      # CLI and web interfaces
│   └── extensions/      # API and file integration capabilities
├── examples/            # Sample English programs
├── docs/                # Documentation
└── tools/               # Development and demo tools
```

## Future Directions

- **Optimization**: Improving bytecode efficiency
- **Language Support**: Extending to other natural languages
- **IDE Integration**: Building plugins for popular code editors
- **Enhanced Error Messages**: Providing more helpful feedback
- **Advanced Libraries**: Adding domain-specific capabilities

## Contributing

We welcome contributions to enhance and expand the English Programming system! See our contributing guidelines for more details.

## License

This project is open source and available under the MIT License.

---

*English Programming: Making coding accessible to everyone*
