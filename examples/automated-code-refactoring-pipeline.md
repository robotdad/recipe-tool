Build a recipe that analyzes a Python codebase, identifies issues, and performs automated refactoring:

1. Scan all Python files in the 'src' directory and its subdirectories.
2. For each file:
   - Run static code analysis to identify code smells, complexity issues, and potential bugs
   - Calculate code quality metrics (cyclomatic complexity, maintainability index, etc.)
   - Check for PEP 8 compliance
   - Identify unused imports and variables
3. Generate a prioritized list of files needing refactoring based on quality metrics.
4. For the top 5 problematic files:
   - Use an LLM to suggest code improvements
   - Generate refactored versions with comments explaining changes
   - Run tests to ensure functionality is preserved
5. Create before/after comparisons for each refactored file.
6. If any refactoring breaks tests, revert to original and flag for manual review.
7. Create a comprehensive report with:
   - Overall codebase health metrics
   - Files analyzed and issues found
   - Refactoring performed and improvements made
   - Recommendations for further improvements
8. Send a notification when the process is complete with a summary of changes.

The entire process should run without human intervention unless critical issues are encountered.
