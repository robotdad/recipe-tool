# Technical Notes

This directory contains technical notes on specific aspects of the Recipe Executor app implementation. These documents provide deeper insights into how certain features work and explain the reasoning behind implementation decisions.

## Available Notes

- [Recipe Format Handling](recipe_format_handling.md): Details on how the app processes different recipe formats and extracts content from the context.
- [Fixes and Improvements](fixes_and_improvements.md): Information about recent fixes and improvements, including path resolution and Gradio integration.
- [Path Resolution Fixes](path_resolution_fixes.md): Comprehensive guide to fixes for path resolution issues in the app.

## Purpose

These technical notes serve several purposes:

1. **Knowledge Preservation**: Document implementation details that might not be obvious from the code
2. **Troubleshooting**: Provide in-depth information for debugging complex issues
3. **Onboarding**: Help new developers understand the system more quickly
4. **Decision Records**: Explain why certain implementation approaches were chosen

## When to Add a New Technical Note

Consider adding a new technical note when:

1. You implement a complex feature that requires special handling
2. You fix a non-trivial bug that required deep understanding of the system
3. You make a significant architectural decision
4. You discover something about the system that isn't documented elsewhere

## Format

Technical notes should include:

1. A clear description of the feature, issue, or component
2. Any relevant code snippets or examples
3. Explanation of design decisions and trade-offs
4. Known limitations or edge cases
5. Tips for debugging related issues