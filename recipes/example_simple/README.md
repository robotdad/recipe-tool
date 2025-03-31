# Simple Recipe Example

## Overview

This directory contains a minimal example of how to use Recipe Executor with a simple recipe. It demonstrates the basic workflow of reading a specification, generating code with an LLM, and writing the output to a file.

## Contents

- `test_recipe.md` - A simple recipe that demonstrates the basic workflow
- `specs/sample_spec.txt` - A minimal specification for generating a Python script

## How It Works

The recipe in `test_recipe.md` follows this process:

1. **Read Specification**: Reads the content of `specs/sample_spec.txt`
2. **Generate Code**: Uses an LLM to generate a Python script based on the specification
3. **Write Output**: Writes the generated code to the output directory

## Usage

Run the recipe with:

```bash
python recipe_executor/main.py recipes/example_simple/test_recipe.md
```

This will generate a Python script in the `output` directory that prints "Hello, Test!" when executed.

## Learning Outcomes

This example teaches you:

1. The basic structure of a recipe file
2. How to read input specifications
3. How to prompt an LLM to generate code
4. How to write the generated output to a file

This is an ideal starting point for beginners to understand the core functionality of Recipe Executor before moving on to more complex examples.