"""
Hero Section Agent for Portfolio Builder.

Generates content for the hero/landing section of the portfolio.
"""

import json
from typing import Dict, Any

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import HERO_SECTION_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import safe_json_parse

logger = get_logger("hero_section")


def hero_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate hero section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    logger.info("Generating hero section content...")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    
    # Use LLM to generate content
    logger.info("--- LLM: Attempting to generate hero content ---")
    content = {}
    llm_success = False
    
    try:
        llm = get_fast_llm(temperature=0.7)
        
        prompt = HERO_SECTION_PROMPT.format(
            resume_data=json.dumps(resume_data, indent=2, default=str),
            website_plan=json.dumps(website_plan, indent=2, default=str),
            style=website_plan.get("style", "modern")
        )
        
        response = llm.invoke(prompt)
        content = safe_json_parse(response.content, default={})
        
        if content:
            llm_success = True
            logger.info("  [LLM] SUCCESS: Got hero content from LLM")
            logger.info(f"  [LLM] headline: {content.get('headline', 'Not provided')}")
            logger.info(f"  [LLM] tagline: {content.get('tagline', 'Not provided')[:50] + '...' if content.get('tagline') else 'Not provided'}")
        else:
            logger.warning("  [LLM] WARNING: LLM returned empty content")
        
    except Exception as e:
        logger.error(f"  [LLM] ERROR: {e}")
    
    # Apply defaults if needed (track what comes from LLM vs defaults)
    name = resume_data.get("name", "Developer")
    content = _apply_hero_defaults(content, resume_data, website_plan, llm_success)
    
    section_content = SectionContent(
        section_name="hero",
        content=content,
        generated=True,
        order=0
    )
    
    logger.info(f"--- RESULT: Generated hero for: {name} ---")
    logger.info(f"  Content source: {'Primarily LLM' if llm_success else 'Primarily DEFAULTS'}")
    
    return {
        "sections_content": [section_content],
        "current_node": "hero_section"
    }


def _apply_hero_defaults(content: Dict, resume_data: Dict, website_plan: Dict, llm_success: bool) -> Dict:
    """Apply default values for missing hero content."""
    name = resume_data.get("name", "Developer")
    
    defaults = {
        "headline": _generate_headline(resume_data),
        "tagline": _generate_tagline(resume_data),
        "greeting": "Hi, I'm",
        "cta_primary": {
            "text": "View My Work",
            "target_section": "projects" if resume_data.get("projects") else "about"
        },
        "cta_secondary": {
            "text": "Get In Touch",
            "action": "scroll_to_contact"
        },
        "background_style": "gradient" if website_plan.get("use_animations") else "solid",
        "show_social_links": bool(resume_data.get("github") or resume_data.get("linkedin")),
        "typing_animation_texts": _generate_typing_texts(resume_data)
    }
    
    # Merge with LLM content, logging source
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
            if not llm_success:
                logger.info(f"  [DEFAULT] {key}: using default value")
    
    return content


def _generate_headline(resume_data: Dict) -> str:
    """Generate a headline from resume data."""
    # Check for role in experience
    experience = resume_data.get("experience", [])
    if experience and experience[0].get("role"):
        return experience[0]["role"]
    
    # Check for relevant skills
    skills = resume_data.get("skills", [])
    dev_keywords = ["react", "python", "javascript", "developer", "engineer"]
    design_keywords = ["figma", "ui", "ux", "design"]
    data_keywords = ["data", "machine learning", "ai", "analytics"]
    
    skills_lower = [s.lower() for s in skills]
    
    if any(kw in skill for skill in skills_lower for kw in dev_keywords):
        return "Software Developer"
    elif any(kw in skill for skill in skills_lower for kw in design_keywords):
        return "UI/UX Designer"
    elif any(kw in skill for skill in skills_lower for kw in data_keywords):
        return "Data Scientist"
    
    return "Developer & Creator"


def _generate_tagline(resume_data: Dict) -> str:
    """Generate a tagline from resume data."""
    summary = resume_data.get("summary")
    if summary:
        # Use first sentence or first 150 chars
        first_sentence = summary.split('.')[0]
        if len(first_sentence) <= 150:
            return first_sentence + "."
        return first_sentence[:147] + "..."
    
    skills = resume_data.get("skills", [])[:3]
    if skills:
        return f"Passionate about building with {', '.join(skills)}."
    
    return "Building digital experiences that make a difference."


def _generate_typing_texts(resume_data: Dict) -> list:
    """Generate texts for typing animation."""
    texts = []
    
    experience = resume_data.get("experience", [])
    if experience:
        texts.append(experience[0].get("role", "Developer"))
    
    skills = resume_data.get("skills", [])[:3]
    for skill in skills:
        if len(skill) < 20:  # Only short skills
            texts.append(f"{skill} Developer")
    
    if not texts:
        texts = ["Developer", "Creator", "Problem Solver"]
    
    return texts[:4]  # Max 4 items
