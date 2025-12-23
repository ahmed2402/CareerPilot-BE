"""
File Service for Portfolio Builder.

Handles file I/O operations for generated portfolio sites.
"""

from pathlib import Path
from typing import List, Optional, Dict
import shutil
import json

from portfolio_builder.core.state import GeneratedCode
from portfolio_builder.utils.file_utils import (
    get_project_path,
    create_project_structure,
    write_file,
    create_zip,
    cleanup_project,
    list_project_files,
    ensure_storage_dirs
)


class FileService:
    """Service for managing generated portfolio files."""
    
    def __init__(self):
        ensure_storage_dirs()
    
    def save_generated_site(
        self, 
        project_id: str, 
        files: List[GeneratedCode]
    ) -> str:
        """
        Save all generated files to disk.
        
        Args:
            project_id: Unique project identifier
            files: List of generated code files
            
        Returns:
            Path to the project directory
        """
        # Create project structure
        folders = create_project_structure(project_id)
        project_path = folders['root']
        
        # Write each file
        for file_info in files:
            # Determine the full path
            relative_path = file_info.get('filepath', file_info['filename'])
            file_path = project_path / relative_path
            
            # Write the file
            success = write_file(file_path, file_info['content'])
            if not success:
                print(f"Warning: Failed to write {file_path}")
        
        # Save metadata
        metadata = {
            'project_id': project_id,
            'file_count': len(files),
            'files': [f['filename'] for f in files]
        }
        write_file(
            project_path / '.portfolio_metadata.json',
            json.dumps(metadata, indent=2)
        )
        
        return str(project_path)
    
    def get_generated_site_path(self, project_id: str) -> Optional[str]:
        """
        Get the path to a generated site.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Path to project directory or None if doesn't exist
        """
        project_path = get_project_path(project_id)
        
        if project_path.exists():
            return str(project_path)
        
        return None
    
    def create_download_zip(self, project_id: str) -> Optional[str]:
        """
        Create a downloadable ZIP of the project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Path to ZIP file or None if error
        """
        zip_path = create_zip(project_id)
        
        if zip_path:
            return str(zip_path)
        
        return None
    
    def cleanup(self, project_id: str) -> bool:
        """
        Remove project files.
        
        Args:
            project_id: Project identifier
            
        Returns:
            True if successful
        """
        return cleanup_project(project_id)
    
    def get_file_list(self, project_id: str) -> List[Dict[str, str]]:
        """
        Get list of files in a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of file info dicts
        """
        return list_project_files(project_id)
    
    def read_generated_file(
        self, 
        project_id: str, 
        relative_path: str
    ) -> Optional[str]:
        """
        Read a specific file from a generated project.
        
        Args:
            project_id: Project identifier
            relative_path: Path relative to project root
            
        Returns:
            File content or None if not found
        """
        project_path = get_project_path(project_id)
        file_path = project_path / relative_path
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
        
        return None
    
    def update_generated_file(
        self, 
        project_id: str, 
        relative_path: str,
        content: str
    ) -> bool:
        """
        Update a specific file in a generated project.
        
        Args:
            project_id: Project identifier
            relative_path: Path relative to project root
            content: New file content
            
        Returns:
            True if successful
        """
        project_path = get_project_path(project_id)
        file_path = project_path / relative_path
        
        return write_file(file_path, content)


# Singleton instance
_file_service: Optional[FileService] = None


def get_file_service() -> FileService:
    """Get the singleton FileService instance."""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service
