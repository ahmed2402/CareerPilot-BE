"""
Projects Section Agent for Portfolio Builder.

Generates content for the projects showcase section of the portfolio.
"""

import json
from typing import Dict, Any, List

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import PROJECTS_SECTION_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import safe_json_parse

logger = get_logger("projects_section")


def projects_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate projects section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    logger.info("Generating projects section content...")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    projects = resume_data.get("projects", [])
    
    if not projects:
        logger.info("No projects found, skipping section")
        return {
            "sections_content": [],
            "current_node": "projects_section"
        }
    
    logger.info("--- LLM: Attempting to generate projects content ---")
    
    # Use LLM to enhance project descriptions
    try:
        llm = get_fast_llm(temperature=0.6)
        
        prompt = PROJECTS_SECTION_PROMPT.format(
            resume_data=json.dumps(resume_data, indent=2, default=str),
            website_plan=json.dumps(website_plan, indent=2, default=str),
            style=website_plan.get("style", "modern")
        )
        
        response = llm.invoke(prompt)
        content = safe_json_parse(response.content, default={})
        
    except Exception as e:
        logger.error(f"  [LLM] ERROR: {e}")
        content = {}
    
    llm_success = bool(content)
    if llm_success:
        logger.info("  [LLM] SUCCESS: Got projects content from LLM")
    else:
        logger.warning("  [LLM] WARNING: Using defaults for projects content")
    
    # Apply defaults
    content = _apply_projects_defaults(content, resume_data, website_plan)
    
    section_content = SectionContent(
        section_name="projects",
        content=content,
        generated=True,
        order=4
    )
    
    logger.info(f"--- RESULT: {len(projects)} projects, source: {'LLM' if llm_success else 'DEFAULTS'} ---")
    
    return {
        "sections_content": [section_content],
        "current_node": "projects_section"
    }


def _apply_projects_defaults(content: Dict, resume_data: Dict, website_plan: Dict) -> Dict:
    """Apply default values for missing projects content."""
    projects = resume_data.get("projects", [])
    
    # Process projects
    processed_projects = []
    for i, project in enumerate(projects):
        processed = {
            "title": project.get("title", f"Project {i+1}"),
            "description": project.get("description", "An amazing project."),
            "technologies": project.get("technologies", []),
            "image_placeholder": f"project-{i+1}",
            "links": {
                "live": project.get("link"),
                "github": project.get("github_link")
            },
            "featured": i < 3,  # First 3 are featured
            "category": _categorize_project(project)
        }
        processed_projects.append(processed)
    
    # Get unique categories
    categories = list(set(p["category"] for p in processed_projects))
    
    defaults = {
        "title": "Featured Projects",
        "subtitle": "Some things I've built",
        "projects": processed_projects,
        "layout": "grid",
        "show_filters": len(categories) > 1,
        "filter_categories": ["All"] + categories
    }
    
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
    
    return content


def _categorize_project(project: Dict) -> str:
    """Categorize a project based on its technologies."""
    technologies = [t.lower() for t in project.get("technologies", [])]
    description = project.get("description", "").lower()
    title = project.get("title", "").lower()
    
    all_text = " ".join(technologies + [description, title])
    
    # Check for categories
    if any(kw in all_text for kw in ["react", "vue", "angular", "next", "frontend", "ui", "website"]):
        return "Web App"
    elif any(kw in all_text for kw in ["mobile", "ios", "android", "react native", "flutter"]):
        return "Mobile"
    elif any(kw in all_text for kw in ["machine learning", "ml", "ai", "data", "tensorflow", "pytorch"]):
        return "AI/ML"
    elif any(kw in all_text for kw in ["api", "backend", "server", "microservice"]):
        return "Backend"
    elif any(kw in all_text for kw in ["game", "unity", "unreal"]):
        return "Game"
    else:
        return "Other"
