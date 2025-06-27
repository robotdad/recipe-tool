"""Package handler for .docpack files.

Handles creation and extraction of .docpack files which are zip archives
containing an outline.json file and associated resource files.
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DocpackHandler:
    """Handles .docpack file creation and extraction."""

    @staticmethod
    def create_package(outline_data: Dict[str, Any], resource_files: List[Path], output_path: Path) -> None:
        """Create a .docpack file from outline data and resource files.

        Args:
            outline_data: The outline JSON data
            resource_files: List of resource file paths to include
            output_path: Where to save the .docpack file
        """
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Always include outline.json
            zf.writestr("outline.json", json.dumps(outline_data, indent=2))

            # Add resource files with their original names
            for resource_file in resource_files:
                if resource_file.exists():
                    zf.write(resource_file, resource_file.name)

    @staticmethod
    def extract_package(package_path: Path, extract_dir: Path) -> Tuple[Dict[str, Any], List[Path]]:
        """Extract a .docpack file to a directory.

        Args:
            package_path: Path to the .docpack file
            extract_dir: Directory to extract to

        Returns:
            Tuple of (outline_data, list_of_resource_file_paths)
        """
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(package_path, "r") as zf:
            zf.extractall(extract_dir)

        # Read outline.json
        outline_path = extract_dir / "outline.json"
        if not outline_path.exists():
            raise ValueError("Package does not contain outline.json")

        with open(outline_path, "r") as f:
            outline_data = json.load(f)

        # Find all other files (resources)
        resource_files = [f for f in extract_dir.iterdir() if f.name != "outline.json"]

        return outline_data, resource_files

    @staticmethod
    def validate_package(package_path: Path) -> bool:
        """Validate that a file is a valid .docpack.

        Args:
            package_path: Path to check

        Returns:
            True if valid .docpack, False otherwise
        """
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                files = zf.namelist()
                return "outline.json" in files
        except zipfile.BadZipFile:
            return False
