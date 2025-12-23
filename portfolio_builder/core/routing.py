"""
Conditional Routing Logic for Portfolio Builder LangGraph Workflow.

Determines which sections to generate and handles workflow branching.
"""

from typing import List, Literal
from portfolio_builder.core.state import PortfolioBuilderState


def route_to_sections(state: PortfolioBuilderState) -> List[str]:
    """
    Determine which section agents to route to based on the website plan.
    
    This is used as a conditional edge function to enable parallel
    execution of section generators.
    
    Args:
        state: Current workflow state with website_plan
        
    Returns:
        List of section node names to execute
    """
    sections_to_generate = state.get("sections_to_generate", [])
    
    if not sections_to_generate:
        # If no sections specified, go directly to aggregation
        return ["aggregate_sections"]
    
    # Map section names to node names
    section_node_map = {
        "hero": "hero_section",
        "about": "about_section",
        "skills": "skills_section",
        "projects": "projects_section",
        "experience": "experience_section",
        "contact": "contact_section"
    }
    
    nodes_to_execute = []
    for section in sections_to_generate:
        node_name = section_node_map.get(section.lower())
        if node_name:
            nodes_to_execute.append(node_name)
    
    return nodes_to_execute if nodes_to_execute else ["aggregate_sections"]


def should_validate(state: PortfolioBuilderState) -> Literal["validate", "skip_validation"]:
    """
    Determine if generated code should be validated.
    
    Args:
        state: Current workflow state
        
    Returns:
        "validate" or "skip_validation"
    """
    generated_files = state.get("generated_files", [])
    
    # Always validate if we have files
    if generated_files:
        return "validate"
    
    return "skip_validation"


def should_revalidate(state: PortfolioBuilderState) -> Literal["regenerate", "assemble", "assemble_with_warnings"]:
    """
    Determine next step after validation.
    
    Args:
        state: Current workflow state with validation_result
        
    Returns:
        - "regenerate": Go back to code generator to fix issues
        - "assemble": Proceed to assembly (validation passed)
        - "assemble_with_warnings": Proceed with warnings (max attempts reached)
    """
    validation_result = state.get("validation_result", {})
    validation_attempts = state.get("validation_attempts", 0)
    max_attempts = state.get("max_validation_attempts", 3)
    
    is_valid = validation_result.get("is_valid", False)
    errors = validation_result.get("errors", [])
    
    if is_valid:
        return "assemble"
    
    if validation_attempts < max_attempts and errors:
        # Still have attempts left and there are errors to fix
        return "regenerate"
    
    # Max attempts reached or no fixable errors
    return "assemble_with_warnings"


def check_resume_parsed(state: PortfolioBuilderState) -> Literal["continue", "error"]:
    """
    Check if resume was parsed successfully.
    
    Args:
        state: Current workflow state
        
    Returns:
        "continue" or "error"
    """
    resume_parsed = state.get("resume_parsed", {})
    parsing_confidence = state.get("parsing_confidence", 0.0)
    
    # Need at least a name and some confidence
    if resume_parsed.get("name") and parsing_confidence > 0.1:
        return "continue"
    
    return "error"


def get_available_sections(state: PortfolioBuilderState) -> List[str]:
    """
    Get list of sections that can be generated based on resume data.
    
    Args:
        state: Current workflow state
        
    Returns:
        List of available section names
    """
    resume_data = state.get("resume_parsed", {})
    
    available = ["hero", "about", "contact"]  # Always available
    
    if resume_data.get("skills"):
        available.append("skills")
    
    if resume_data.get("projects"):
        available.append("projects")
    
    if resume_data.get("experience"):
        available.append("experience")
    
    if resume_data.get("education"):
        available.append("education")
    
    if resume_data.get("certifications"):
        available.append("certifications")
    
    return available
