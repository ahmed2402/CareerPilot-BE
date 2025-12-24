"""
About Section Agent for Portfolio Builder.

Generates content for the about/bio section of the portfolio.
"""

import json
from typing import Dict, Any

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import ABOUT_SECTION_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import safe_json_parse

logger = get_logger("about_section")


def about_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate about section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    logger.info("Generating about section content...")
    logger.info("--- LLM: Attempting to generate about content ---")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    
    # Use LLM to generate content
    try:
        llm = get_fast_llm(temperature=0.7)
        
        prompt = ABOUT_SECTION_PROMPT.format(
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
        logger.info("  [LLM] SUCCESS: Got about content from LLM")
    else:
        logger.warning("  [LLM] WARNING: Using defaults for about content")
    
    # Apply defaults
    content = _apply_about_defaults(content, resume_data, website_plan)
    
    section_content = SectionContent(
        section_name="about",
        content=content,
        generated=True,
        order=1
    )
    
    logger.info(f"--- RESULT: Content source: {'Primarily LLM' if llm_success else 'Primarily DEFAULTS'} ---")
    
    return {
        "sections_content": [section_content],
        "current_node": "about_section"
    }


def _apply_about_defaults(content: Dict, resume_data: Dict, website_plan: Dict) -> Dict:
    """Apply default values for missing about content."""
    name = resume_data.get("name", "Developer")
    
    defaults = {
        "title": "About Me",
        "bio_paragraphs": _generate_bio_paragraphs(resume_data),
        "key_facts": _generate_key_facts(resume_data),
        "profile_image_placeholder": True,
        "layout": "text-left"
    }
    
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
    
    return content


def _generate_bio_paragraphs(resume_data: Dict) -> list:
    """Generate bio paragraphs from resume data."""
    paragraphs = []
    name = resume_data.get("name", "a developer")
    
    # First paragraph - intro
    summary = resume_data.get("summary", "")
    if summary:
        paragraphs.append(summary)
    else:
        experience = resume_data.get("experience", [])
        if experience:
            role = experience[0].get("role", "professional")
            company = experience[0].get("company", "")
            intro = f"I'm {name}, a {role}"
            if company:
                intro += f" currently working at {company}"
            intro += "."
            paragraphs.append(intro)
        else:
            paragraphs.append(f"I'm {name}, passionate about creating impactful digital solutions.")
    
    # Second paragraph - skills/expertise
    skills = resume_data.get("skills", [])
    if skills:
        skill_text = ", ".join(skills[:5])
        paragraphs.append(f"My expertise includes {skill_text}, and I'm always eager to learn new technologies.")
    
    # Third paragraph - interests/goals
    interests = resume_data.get("interests", [])
    if interests:
        interest_text = ", ".join(interests[:3])
        paragraphs.append(f"When I'm not coding, you can find me exploring {interest_text}.")
    
    return paragraphs if paragraphs else ["Passionate about creating amazing digital experiences."]


def _generate_key_facts(resume_data: Dict) -> list:
    """Generate key facts for about section."""
    facts = []
    
    # Experience years (estimate from positions)
    experience = resume_data.get("experience", [])
    if experience:
        facts.append({
            "icon": "briefcase",
            "label": "Experience",
            "value": f"{len(experience)}+ Roles"
        })
    
    # Projects count
    projects = resume_data.get("projects", [])
    if projects:
        facts.append({
            "icon": "code",
            "label": "Projects",
            "value": f"{len(projects)}+ Projects"
        })
    
    # Education
    education = resume_data.get("education", [])
    if education:
        degree = education[0].get("degree", "Graduate")
        facts.append({
            "icon": "graduation-cap",
            "label": "Education",
            "value": degree
        })
    
    # Skills count
    skills = resume_data.get("skills", [])
    if skills:
        facts.append({
            "icon": "star",
            "label": "Technologies",
            "value": f"{len(skills)}+ Skills"
        })
    
    return facts[:4]  # Max 4 facts
