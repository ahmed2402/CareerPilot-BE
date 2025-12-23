"""
State Schema for the Portfolio Builder LangGraph Workflow.

This is the MOST CRITICAL component - all nodes read from and write to this shared state.
"""

from typing import TypedDict, List, Optional, Literal, Annotated
from operator import add


class ResumeData(TypedDict, total=False):
    """Structured data extracted from resume."""
    name: str
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    website: Optional[str]
    summary: Optional[str]
    skills: List[str]
    projects: List[dict]  # {title, description, technologies, link, github_link}
    experience: List[dict]  # {company, role, duration, description, highlights}
    education: List[dict]  # {institution, degree, field, year, gpa}
    certifications: List[dict]  # {name, issuer, date, link}
    languages: List[str]
    interests: List[str]


class WebsitePlan(TypedDict, total=False):
    """Website design plan created by the planner agent."""
    style: Literal["minimal", "modern", "creative", "professional", "bold"]
    color_scheme: dict  # {primary, secondary, accent, background, text}
    sections: List[str]  # ["hero", "about", "skills", "projects", "experience", "contact"]
    layout: Literal["single_page", "multi_section"]
    use_animations: bool
    animation_library: Optional[str]  # "framer-motion" or None
    tech_stack: List[str]  # ["react", "tailwind", "framer-motion"]
    font_family: str  # Primary font choice
    dark_mode: bool
    navigation_style: Literal["fixed", "sticky", "static"]


class SectionContent(TypedDict):
    """Content generated for a specific section."""
    section_name: str
    content: dict  # Section-specific content structure
    generated: bool
    order: int  # Display order in the website


class GeneratedCode(TypedDict):
    """A generated code file."""
    filename: str
    filepath: str  # Relative path from project root
    content: str
    component_type: Literal["component", "page", "style", "config", "util", "asset"]


class ValidationError(TypedDict):
    """A single validation error."""
    file: str
    line: Optional[int]
    message: str
    severity: Literal["error", "warning", "info"]
    rule: Optional[str]


class ValidationResult(TypedDict):
    """Result of code validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    fixed_files: List[str]  # Files that were auto-fixed


class PortfolioBuilderState(TypedDict, total=False):
    """
    Complete state for the Portfolio Builder LangGraph workflow.
    
    This state flows through all nodes in the graph:
    START → Resume Parser → Website Planner → Section Generators → 
    Code Generator → Validator → Assembler → END
    """
    
    # ============ INPUT ============
    user_prompt: str  # User's preferences and requirements
    resume_text: str  # Raw resume text (from PDF or direct input)
    resume_file_path: Optional[str]  # Path to uploaded resume file
    
    # ============ RESUME PARSING ============
    resume_parsed: ResumeData  # Structured resume data
    parsing_confidence: float  # 0.0 to 1.0 confidence in parsing
    
    # ============ PLANNING ============
    website_plan: WebsitePlan  # Design decisions
    sections_to_generate: List[str]  # Sections that will be generated
    
    # ============ SECTION GENERATION ============
    sections_content: Annotated[List[SectionContent], add]  # Generated section content
    current_section_index: int  # For tracking progress
    
    # ============ CODE GENERATION ============
    generated_files: List[GeneratedCode]  # All generated code files
    project_structure: dict  # Folder structure metadata
    
    # ============ VALIDATION ============
    validation_result: ValidationResult
    validation_attempts: int  # Current attempt count
    max_validation_attempts: int  # Maximum retry attempts (default: 3)
    
    # ============ ASSEMBLY ============
    project_id: str  # Unique identifier for this generation
    output_path: str  # Path to generated project folder
    preview_url: Optional[str]  # URL for live preview
    zip_path: Optional[str]  # Path to downloadable ZIP
    
    # ============ WORKFLOW CONTROL ============
    errors: List[str]  # Any errors encountered
    warnings: List[str]  # Non-critical warnings
    current_node: str  # Current node in the workflow
    workflow_status: Literal["running", "completed", "failed", "paused"]


def create_initial_state(
    user_prompt: str,
    resume_text: str,
    resume_file_path: Optional[str] = None,
    project_id: Optional[str] = None
) -> PortfolioBuilderState:
    """
    Create the initial state for starting a portfolio generation workflow.
    
    Args:
        user_prompt: User's preferences and requirements
        resume_text: Raw resume text
        resume_file_path: Optional path to the resume file
        project_id: Optional unique ID (will be generated if not provided)
    
    Returns:
        Initial PortfolioBuilderState ready for workflow execution
    """
    import uuid
    
    return PortfolioBuilderState(
        # Input
        user_prompt=user_prompt,
        resume_text=resume_text,
        resume_file_path=resume_file_path,
        
        # Default empty structures
        resume_parsed=ResumeData(),
        parsing_confidence=0.0,
        website_plan=WebsitePlan(),
        sections_to_generate=[],
        sections_content=[],
        current_section_index=0,
        generated_files=[],
        project_structure={},
        
        # Validation
        validation_result=ValidationResult(
            is_valid=False,
            errors=[],
            warnings=[],
            fixed_files=[]
        ),
        validation_attempts=0,
        max_validation_attempts=3,
        
        # Assembly
        project_id=project_id or str(uuid.uuid4())[:8],
        output_path="",
        preview_url=None,
        zip_path=None,
        
        # Workflow control
        errors=[],
        warnings=[],
        current_node="start",
        workflow_status="running"
    )
