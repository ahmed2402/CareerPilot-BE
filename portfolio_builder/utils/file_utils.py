"""
File Utilities for Portfolio Builder.

Functions for file system operations, project structure creation, and packaging.
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime


# Base storage paths
STORAGE_BASE = Path(__file__).parent.parent / "storage"
UPLOADS_DIR = STORAGE_BASE / "uploads"
GENERATED_SITES_DIR = STORAGE_BASE / "generated_sites"
TEMP_DIR = STORAGE_BASE / "temp"


def ensure_storage_dirs():
    """Ensure all storage directories exist."""
    for dir_path in [UPLOADS_DIR, GENERATED_SITES_DIR, TEMP_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_project_path(project_id: str) -> Path:
    """
    Get the path for a generated project.
    
    Args:
        project_id: Unique project identifier
        
    Returns:
        Path to project directory
    """
    ensure_storage_dirs()
    return GENERATED_SITES_DIR / project_id


def create_project_structure(project_id: str) -> Dict[str, Path]:
    """
    Create the React project folder structure.
    
    Args:
        project_id: Unique project identifier
        
    Returns:
        Dictionary mapping folder names to their paths
    """
    project_path = get_project_path(project_id)
    
    # Define folder structure
    folders = {
        'root': project_path,
        'src': project_path / 'src',
        'components': project_path / 'src' / 'components',
        'assets': project_path / 'src' / 'assets',
        'public': project_path / 'public',
    }
    
    # Create all folders
    for name, path in folders.items():
        path.mkdir(parents=True, exist_ok=True)
    
    return folders


def write_file(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to a file.
    
    Args:
        file_path: Path to write to
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False


def read_file(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read content from a file.
    
    Args:
        file_path: Path to read from
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content or None if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def create_zip(project_id: str, output_name: Optional[str] = None) -> Optional[Path]:
    """
    Create a ZIP archive of a generated project.
    
    Args:
        project_id: Project identifier
        output_name: Optional custom name for ZIP file
        
    Returns:
        Path to ZIP file or None if error
    """
    ensure_storage_dirs()
    
    project_path = get_project_path(project_id)
    if not project_path.exists():
        print(f"Project directory does not exist: {project_path}")
        return None
    
    # Generate ZIP filename
    if output_name:
        zip_name = f"{output_name}.zip"
    else:
        zip_name = f"portfolio_{project_id}.zip"
    
    zip_path = TEMP_DIR / zip_name
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                # Skip node_modules if it exists
                if 'node_modules' in dirs:
                    dirs.remove('node_modules')
                
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        return None


def cleanup_project(project_id: str) -> bool:
    """
    Remove a project directory and its files.
    
    Args:
        project_id: Project identifier
        
    Returns:
        True if successful
    """
    project_path = get_project_path(project_id)
    
    try:
        if project_path.exists():
            shutil.rmtree(project_path)
        return True
    except Exception as e:
        print(f"Error cleaning up project {project_id}: {e}")
        return False


def cleanup_old_files(max_age_hours: int = 24):
    """
    Clean up old generated files and temp files.
    
    Args:
        max_age_hours: Delete files older than this many hours
    """
    ensure_storage_dirs()
    
    now = datetime.now().timestamp()
    max_age_seconds = max_age_hours * 3600
    
    # Clean temp directory
    for item in TEMP_DIR.iterdir():
        try:
            if now - item.stat().st_mtime > max_age_seconds:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        except Exception as e:
            print(f"Error cleaning up {item}: {e}")


def save_upload(file_content: bytes, filename: str, project_id: str) -> Path:
    """
    Save an uploaded file.
    
    Args:
        file_content: File bytes
        filename: Original filename
        project_id: Project identifier
        
    Returns:
        Path to saved file
    """
    ensure_storage_dirs()
    
    # Create project-specific upload folder
    upload_dir = UPLOADS_DIR / project_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_dir / filename
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return file_path


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return Path(filename).suffix.lower()


def is_valid_resume_file(filename: str) -> bool:
    """Check if file is a valid resume format."""
    valid_extensions = ['.pdf', '.txt', '.doc', '.docx']
    return get_file_extension(filename) in valid_extensions


def list_project_files(project_id: str) -> List[Dict[str, str]]:
    """
    List all files in a generated project.
    
    Args:
        project_id: Project identifier
        
    Returns:
        List of file info dicts with path and size
    """
    project_path = get_project_path(project_id)
    files = []
    
    if not project_path.exists():
        return files
    
    for root, _, filenames in os.walk(project_path):
        for filename in filenames:
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(project_path)
            files.append({
                'path': str(relative_path),
                'absolute_path': str(file_path),
                'size': file_path.stat().st_size,
                'extension': get_file_extension(filename)
            })
    
    return files
