"""
Auto Portfolio Builder - Main Entry Point

This module provides the main interface for generating portfolio websites
from user prompts and resume data using a LangGraph multi-agent workflow.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from portfolio_builder.core.state import create_initial_state, PortfolioBuilderState
from portfolio_builder.core.graph import get_workflow
from portfolio_builder.services.resume_parser import get_resume_parser_service
from portfolio_builder.utils.helpers import generate_project_id


def generate_portfolio(
    user_prompt: str,
    resume_text: Optional[str] = None,
    resume_file_path: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a complete portfolio website from user prompt and resume.
    
    This is the main entry point for the portfolio builder workflow.
    
    Args:
        user_prompt: User's preferences and requirements for the portfolio
        resume_text: Raw resume text (if already extracted)
        resume_file_path: Path to resume file (PDF, TXT, DOCX)
        project_id: Optional custom project ID
        
    Returns:
        Dictionary with:
        - success: Whether generation was successful
        - project_id: Unique identifier for this generation
        - output_path: Path to generated project folder
        - preview_url: URL/path for preview
        - zip_path: Path to downloadable ZIP
        - errors: List of any errors encountered
        - warnings: List of warnings
        
    Raises:
        ValueError: If neither resume_text nor resume_file_path is provided
    """
    print("=" * 60)
    print("[*] Auto Portfolio Builder")
    print("=" * 60)
    
    # Validate input
    if not resume_text and not resume_file_path:
        raise ValueError("Either resume_text or resume_file_path must be provided")
    
    # Extract resume text from file if needed
    if not resume_text and resume_file_path:
        print(f"[FILE] Parsing resume from: {resume_file_path}")
        parser_service = get_resume_parser_service()
        resume_text = parser_service.extract_text_from_file(resume_file_path)
    
    # Generate project ID
    if not project_id:
        project_id = generate_project_id()
    
    print(f"[ID] Project ID: {project_id}")
    print(f"[PROMPT] User Prompt: {user_prompt[:100]}..." if len(user_prompt) > 100 else f"[PROMPT] User Prompt: {user_prompt}")
    print(f"[RESUME] Resume Text: {len(resume_text)} characters")
    print("-" * 60)
    
    # Create initial state
    initial_state = create_initial_state(
        user_prompt=user_prompt,
        resume_text=resume_text,
        resume_file_path=resume_file_path,
        project_id=project_id
    )
    
    # Get and run the workflow
    workflow = get_workflow()
    
    print("[RUNNING] Starting workflow execution...")
    print("-" * 60)
    
    try:
        # Execute the workflow
        result = workflow.invoke(initial_state)
        
        print("-" * 60)
        print("[OK] Workflow execution complete!")
        
        # Build response
        return {
            "success": result.get("workflow_status") in ["completed", "completed_with_errors"],
            "project_id": project_id,
            "output_path": result.get("output_path"),
            "preview_url": result.get("preview_url"),
            "zip_path": result.get("zip_path"),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
            "validation_result": result.get("validation_result", {}),
            "website_plan": result.get("website_plan", {}),
            "resume_parsed": result.get("resume_parsed", {})
        }
        
    except Exception as e:
        print(f"[ERROR] Workflow error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "project_id": project_id,
            "output_path": None,
            "preview_url": None,
            "zip_path": None,
            "errors": [str(e)],
            "warnings": []
        }


def generate_portfolio_from_file(
    resume_path: str,
    user_prompt: str = "Create a modern, professional portfolio website"
) -> Dict[str, Any]:
    """
    Convenience function to generate portfolio from a resume file.
    
    Args:
        resume_path: Path to resume file (PDF, TXT, DOCX)
        user_prompt: Optional preferences for the portfolio
        
    Returns:
        Same as generate_portfolio()
    """
    return generate_portfolio(
        user_prompt=user_prompt,
        resume_file_path=resume_path
    )


def generate_portfolio_from_text(
    resume_text: str,
    user_prompt: str = "Create a modern, professional portfolio website"
) -> Dict[str, Any]:
    """
    Convenience function to generate portfolio from resume text.
    
    Args:
        resume_text: Raw resume text
        user_prompt: Optional preferences for the portfolio
        
    Returns:
        Same as generate_portfolio()
    """
    return generate_portfolio(
        user_prompt=user_prompt,
        resume_text=resume_text
    )


# Example usage
if __name__ == "__main__":
    # Generate portfolio
    import time
    start_time = time.time()
    result = generate_portfolio(
        user_prompt="Create a sophisticated, modern portfolio website using my resume data. Use a slate grey background with emerald green accents and white text. Implement a clean bento-grid layout for the project showcase, add staggered reveal animations for page sections, and ensure it is fully responsive with elegant hover effects on all interactive elements.",
        resume_file_path="./Ahmed Raza - AI Engineer.pdf"
    )
    end_time = time.time()
    
    print("\n" + "=" * 60)
    print("[RESULT] GENERATION RESULT")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Project ID: {result['project_id']}")
    print(f"Output Path: {result['output_path']}")
    print(f"ZIP Path: {result['zip_path']}")
    print(f"Preview URL: {result['preview_url']}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result.get('warnings', []))}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
