A simple tool for creating a roll-up file of all of the text files in a directory.

Requirements:

- All text files in the directory should be rolled up into a single file.
- Command line arguments should be used to specify the input directory and the output file.
  - The input directory should be specified with the `--input` argument.
  - The output file should be specified with the `--output` argument.
- The tool should be able to handle subdirectories and roll up all text files in the directory tree.
- An optional argument `--exclude` should be provided to exclude certain files or directories from the roll-up.
  - The `--exclude` argument should accept a comma-separated list of file or directory names to exclude or a wildcard pattern.
- Any non-text files should be ignored.
- The tool should be named `rollup.py`.
