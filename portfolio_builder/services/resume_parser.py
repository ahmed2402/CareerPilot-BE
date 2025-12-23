"""
Resume Parser Service for Portfolio Builder.

Handles extraction of text from various resume formats (PDF, TXT, DOCX).
"""

import os
from pathlib import Path
from typing import Optional, Union
from pypdf import PdfReader


class ResumeParserService:
    """Service for parsing resume files and extracting text."""
    
    SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.doc', '.docx']
    
    def __init__(self):
        pass
    
    def parse_pdf(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid PDF
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if file_path.suffix.lower() != '.pdf':
            raise ValueError(f"Not a PDF file: {file_path}")
        
        try:
            reader = PdfReader(str(file_path))
            text_parts = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            return '\n\n'.join(text_parts)
        
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {e}")
    
    def parse_text(self, file_path: Union[str, Path]) -> str:
        """
        Read text from a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File content
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file with any supported encoding: {file_path}")
    
    def parse_docx(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a DOCX file.
        
        Note: Requires python-docx to be installed.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text content
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DOCX file not found: {file_path}")
        
        try:
            from docx import Document
            
            doc = Document(str(file_path))
            paragraphs = [para.text for para in doc.paragraphs]
            return '\n'.join(paragraphs)
        
        except ImportError:
            raise ImportError(
                "python-docx is required to parse DOCX files. "
                "Install it with: pip install python-docx"
            )
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {e}")
    
    def extract_text_from_file(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a resume file (auto-detects format).
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Extracted text content
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.parse_pdf(file_path)
        elif extension == '.txt':
            return self.parse_text(file_path)
        elif extension in ['.doc', '.docx']:
            return self.parse_docx(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
    
    def extract_text_from_bytes(
        self, 
        file_bytes: bytes, 
        filename: str,
        temp_dir: Optional[Path] = None
    ) -> str:
        """
        Extract text from file bytes (for uploaded files).
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename (for extension detection)
            temp_dir: Optional temp directory for saving
            
        Returns:
            Extracted text content
        """
        import tempfile
        
        extension = Path(filename).suffix.lower()
        
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        # Create a temporary file
        if temp_dir:
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_path = temp_dir / f"temp_resume{extension}"
        else:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=extension, 
                delete=False
            )
            temp_path = Path(temp_file.name)
            temp_file.close()
        
        try:
            # Write bytes to temp file
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
            # Extract text
            text = self.extract_text_from_file(temp_path)
            
            return text
        
        finally:
            # Cleanup temp file
            if temp_path.exists():
                temp_path.unlink()
    
    def is_valid_resume(self, text: str) -> bool:
        """
        Basic validation that text looks like a resume.
        
        Args:
            text: Extracted resume text
            
        Returns:
            True if text appears to be a valid resume
        """
        if not text or len(text.strip()) < 100:
            return False
        
        # Check for common resume keywords
        resume_keywords = [
            'experience', 'education', 'skills', 'work',
            'email', 'phone', 'project', 'resume', 'cv',
            'professional', 'summary', 'objective'
        ]
        
        text_lower = text.lower()
        matches = sum(1 for keyword in resume_keywords if keyword in text_lower)
        
        # Should have at least 2 common resume keywords
        return matches >= 2


# Singleton instance
_resume_parser_service: Optional[ResumeParserService] = None


def get_resume_parser_service() -> ResumeParserService:
    """Get the singleton ResumeParserService instance."""
    global _resume_parser_service
    if _resume_parser_service is None:
        _resume_parser_service = ResumeParserService()
    return _resume_parser_service
