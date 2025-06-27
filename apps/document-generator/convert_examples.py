#!/usr/bin/env python3
"""
Convert existing JSON examples to .docpack format.

This script scans the examples directory, finds JSON outline files and their
associated resource files, then creates .docpack versions of them.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from document_generator_app.package_handler import DocpackHandler


def find_resource_files(example_dir: Path, outline_data: Dict[str, Any]) -> List[Path]:
    """Find resource files referenced in the outline within the example directory."""
    resource_files = []

    if "resources" not in outline_data:
        return resource_files

    for resource in outline_data["resources"]:
        if "path" in resource and resource["path"]:
            # Look for the file in the resources subdirectory
            resource_path = example_dir / "resources" / Path(resource["path"]).name
            if resource_path.exists():
                resource_files.append(resource_path)

    return resource_files


def convert_example(json_path: Path, output_dir: Path) -> None:
    """Convert a single JSON example to .docpack format."""
    print(f"Converting {json_path.name}...")

    # Load the JSON file
    with open(json_path, "r") as f:
        outline_data = json.load(f)

    # Find associated resource files
    example_dir = json_path.parent
    resource_files = find_resource_files(example_dir, outline_data)

    # Create output filename
    example_name = json_path.stem
    docpack_path = output_dir / f"{example_name}.docpack"

    # Create the docpack
    DocpackHandler.create_package(outline_data, resource_files, docpack_path)

    print(f"  ✅ Created {docpack_path.name}")
    if resource_files:
        print(f"     Included {len(resource_files)} resource files:")
        for rf in resource_files:
            print(f"       - {rf.name}")


def main():
    """Convert all example JSON files to .docpack format."""
    print("Converting examples to .docpack format...")

    # Define paths
    script_dir = Path(__file__).parent
    examples_dir = script_dir.parent.parent / "recipes" / "document_generator" / "examples"
    output_dir = examples_dir / "docpacks"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Find all JSON files in examples directory
    json_files = list(examples_dir.glob("*.json"))

    if not json_files:
        print("No JSON example files found.")
        return

    print(f"Found {len(json_files)} JSON example files:")
    for json_file in json_files:
        print(f"  - {json_file.name}")

    print(f"\nConverting to .docpack files in {output_dir}...")

    # Convert each example
    for json_file in json_files:
        try:
            convert_example(json_file, output_dir)
        except Exception as e:
            print(f"  ❌ Error converting {json_file.name}: {str(e)}")

    print(f"\n✅ Conversion complete! Check {output_dir} for .docpack files.")


if __name__ == "__main__":
    main()
