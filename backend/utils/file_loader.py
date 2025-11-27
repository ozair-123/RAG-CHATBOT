import os
from typing import List, Dict
from pathlib import Path


def load_markdown_files(docs_path: str, extensions: List[str]) -> List[Dict]:
    """
    Load all markdown files from a directory recursively.

    Args:
        docs_path: Path to the documents directory
        extensions: List of file extensions to include (e.g., ['.md', '.mdx'])

    Returns:
        List of dictionaries with file_path, relative_path, and content
    """
    files = []
    docs_path_obj = Path(docs_path)

    if not docs_path_obj.exists():
        raise ValueError(f"Path does not exist: {docs_path}")

    if not docs_path_obj.is_dir():
        raise ValueError(f"Path is not a directory: {docs_path}")

    # Walk through directory
    for root, dirs, filenames in os.walk(docs_path):
        for filename in filenames:
            # Check if file has valid extension
            if any(filename.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, docs_path)

                # Read file content
                try:
                    content = read_file_content(file_path)
                    files.append(
                        {
                            "file_path": file_path,
                            "relative_path": relative_path,
                            "content": content,
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not read file {file_path}: {e}")
                    continue

    return files


def read_file_content(file_path: str) -> str:
    """
    Read file content with UTF-8 encoding.

    Args:
        file_path: Path to the file

    Returns:
        File content as string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def get_relative_path(file_path: str, base_path: str) -> str:
    """
    Calculate relative path from base path.

    Args:
        file_path: Full file path
        base_path: Base directory path

    Returns:
        Relative path
    """
    return os.path.relpath(file_path, base_path)
