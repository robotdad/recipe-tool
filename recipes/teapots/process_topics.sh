#!/bin/bash

# Check if virtual environment is already activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
  # Source the virtual environment
  if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
  else
    echo "Warning: Virtual environment not found at .venv/bin/activate"
    echo "Make sure you've run 'make install' or activated the virtual environment manually"
  fi
else
  echo "Using already activated virtual environment: ${VIRTUAL_ENV}"
fi

# Ensure we're in the project root directory
cd "$(dirname "$0")/../.." || exit 1
echo "Working directory: $(pwd)"

# Create output directory if it doesn't exist
mkdir -p output/teapots

# Read the topics from topics.txt and process each one
while IFS= read -r topic || [[ -n "$topic" ]]; do
  # Skip empty lines
  if [ -z "$topic" ]; then
    continue
  fi
  
  echo "Processing topic: $topic"
  
  # Run the command with the current topic
  python recipe_tool.py --execute recipes/document_generator/document-generator-recipe.json \
    outline_file=recipes/teapots/teapot.json \
    output_root="output/teapots" \
    model=azure/o4-mini \
    topic="$topic"
    
  echo "Completed topic: $topic"
  echo "----------------------------------------"
done < recipes/teapots/topics.txt

echo "All topics processed!"