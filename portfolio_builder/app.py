"""
Auto Portfolio Builder - Main Entry Point

This module provides the main interface for generating portfolio websites
from user prompts and resume data using a LangGraph multi-agent workflow.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

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
    print("🚀 Auto Portfolio Builder")
    print("=" * 60)
    
    # Validate input
    if not resume_text and not resume_file_path:
        raise ValueError("Either resume_text or resume_file_path must be provided")
    
    # Extract resume text from file if needed
    if not resume_text and resume_file_path:
        print(f"📄 Parsing resume from: {resume_file_path}")
        parser_service = get_resume_parser_service()
        resume_text = parser_service.extract_text_from_file(resume_file_path)
    
    # Generate project ID
    if not project_id:
        project_id = generate_project_id()
    
    print(f"📝 Project ID: {project_id}")
    print(f"📋 User Prompt: {user_prompt[:100]}..." if len(user_prompt) > 100 else f"📋 User Prompt: {user_prompt}")
    print(f"📄 Resume Text: {len(resume_text)} characters")
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
    
    print("🔄 Starting workflow execution...")
    print("-" * 60)
    
    try:
        # Execute the workflow
        result = workflow.invoke(initial_state)
        
        print("-" * 60)
        print("✅ Workflow execution complete!")
        
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
        print(f"❌ Workflow error: {e}")
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
    # Example with sample resume text
    sample_resume = """
    John Doe
    Full Stack Developer
    Email: john.doe@email.com
    GitHub: github.com/johndoe
    LinkedIn: linkedin.com/in/johndoe
    
    SUMMARY
    Passionate full-stack developer with 5+ years of experience building 
    scalable web applications. Expert in React, Node.js, and cloud technologies.
    
    SKILLS
    - Frontend: React, Vue.js, TypeScript, Tailwind CSS
    - Backend: Node.js, Python, FastAPI, Express
    - Database: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Docker, Kubernetes
    - Tools: Git, GitHub, Figma, VS Code
    
    EXPERIENCE
    
    Senior Software Engineer | Tech Corp | 2021 - Present
    - Led development of microservices architecture serving 1M+ users
    - Implemented CI/CD pipelines reducing deployment time by 60%
    - Mentored junior developers and conducted code reviews
    
    Software Developer | StartupXYZ | 2019 - 2021
    - Built React-based dashboard for data visualization
    - Developed REST APIs using Node.js and Express
    - Optimized database queries improving performance by 40%
    
    PROJECTS
    
    E-Commerce Platform
    Full-stack e-commerce solution with React, Node.js, and Stripe integration
    Technologies: React, Node.js, MongoDB, Stripe
    GitHub: github.com/johndoe/ecommerce
    
    AI Chat Assistant
    Conversational AI assistant using GPT-4 and vector search
    Technologies: Python, FastAPI, OpenAI, Pinecone
    Demo: aichat.johndoe.dev
    
    EDUCATION
    
    B.S. Computer Science | State University | 2019
    GPA: 3.8/4.0
    """
    
    # Generate portfolio
    result = generate_portfolio(
        user_prompt="Create a modern, sleek portfolio with dark mode and subtle animations. Focus on my AI Engineer skills.",
        resume_file_path="./Ahmed Raza - AI Engineer.pdf"
    )
    
    print("\n" + "=" * 60)
    print("📊 GENERATION RESULT")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Project ID: {result['project_id']}")
    print(f"Output Path: {result['output_path']}")
    print(f"ZIP Path: {result['zip_path']}")
    print(f"Preview URL: {result['preview_url']}")
    print(f"Errors: {len(result['errors'])}")
    print(f"Warnings: {len(result.get('warnings', []))}")
