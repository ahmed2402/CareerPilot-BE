"""
Experience Section Agent for Portfolio Builder.

Generates content for the work experience/timeline section of the portfolio.
"""

import json
from typing import Dict, Any

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import EXPERIENCE_SECTION_PROMPT
from portfolio_builder.utils.helpers import safe_json_parse


def experience_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate experience section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    print("[ExperienceSection] Generating experience section content...")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    experience = resume_data.get("experience", [])
    
    if not experience:
        print("[ExperienceSection] No experience found, skipping")
        return {
            "sections_content": [],
            "current_node": "experience_section"
        }
    
    # Use LLM to enhance experience descriptions
    try:
        llm = get_fast_llm(temperature=0.5)
        
        prompt = EXPERIENCE_SECTION_PROMPT.format(
            resume_data=json.dumps(resume_data, indent=2, default=str),
            website_plan=json.dumps(website_plan, indent=2, default=str),
            style=website_plan.get("style", "modern")
        )
        
        response = llm.invoke(prompt)
        content = safe_json_parse(response.content, default={})
        
    except Exception as e:
        print(f"[ExperienceSection] ERROR with LLM: {e}")
        content = {}
    
    # Apply defaults
    content = _apply_experience_defaults(content, resume_data, website_plan)
    
    section_content = SectionContent(
        section_name="experience",
        content=content,
        generated=True,
        order=3
    )
    
    print(f"[ExperienceSection] Generated content for {len(experience)} experiences")
    
    return {
        "sections_content": [section_content],
        "current_node": "experience_section"
    }


def _apply_experience_defaults(content: Dict, resume_data: Dict, website_plan: Dict) -> Dict:
    """Apply default values for missing experience content."""
    experience = resume_data.get("experience", [])
    
    # Process experiences
    processed_experiences = []
    for i, exp in enumerate(experience):
        processed = {
            "company": exp.get("company", f"Company {i+1}"),
            "role": exp.get("role", "Professional"),
            "duration": exp.get("duration", "Present"),
            "location": exp.get("location", ""),
            "description": exp.get("description", ""),
            "highlights": exp.get("highlights", []),
            "technologies": _extract_technologies(exp),
            "logo_placeholder": f"company-{i+1}"
        }
        processed_experiences.append(processed)
    
    style = website_plan.get("style", "modern")
    layout = "timeline" if style in ["modern", "creative"] else "cards"
    
    defaults = {
        "title": "Experience",
        "subtitle": "My professional journey",
        "experiences": processed_experiences,
        "layout": layout,
        "show_company_logos": True
    }
    
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
    
    return content


def _extract_technologies(experience: Dict) -> list:
    """Extract technologies from experience description."""
    description = experience.get("description", "")
    highlights = experience.get("highlights", [])
    
    # Common technologies to look for
    tech_keywords = [
        "React", "Vue", "Angular", "Next.js", "Node.js", "Python", "Java",
        "JavaScript", "TypeScript", "AWS", "GCP", "Azure", "Docker",
        "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "GraphQL",
        "REST", "API", "Machine Learning", "TensorFlow", "PyTorch"
    ]
    
    all_text = (description or "") + " " + " ".join(highlights or [])
    
    found_tech = []
    for tech in tech_keywords:
        if tech.lower() in all_text.lower():
            found_tech.append(tech)
    
    return found_tech[:5]  # Limit to 5
