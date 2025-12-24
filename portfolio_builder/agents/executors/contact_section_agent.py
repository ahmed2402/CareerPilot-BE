"""
Contact Section Agent for Portfolio Builder.

Generates content for the contact/get in touch section of the portfolio.
"""

import json
from typing import Dict, Any

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import CONTACT_SECTION_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import safe_json_parse

logger = get_logger("contact_section")


def contact_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate contact section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    logger.info("Generating contact section content...")
    logger.info("--- LLM: Attempting to generate contact content ---")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    
    # Use LLM to generate content
    try:
        llm = get_fast_llm(temperature=0.7)
        
        prompt = CONTACT_SECTION_PROMPT.format(
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
        logger.info("  [LLM] SUCCESS: Got contact content from LLM")
    else:
        logger.warning("  [LLM] WARNING: Using defaults for contact content")
    
    # Apply defaults
    content = _apply_contact_defaults(content, resume_data, website_plan)
    
    section_content = SectionContent(
        section_name="contact",
        content=content,
        generated=True,
        order=7
    )
    
    logger.info(f"--- RESULT: Content source: {'LLM' if llm_success else 'DEFAULTS'} ---")
    
    return {
        "sections_content": [section_content],
        "current_node": "contact_section"
    }


def _apply_contact_defaults(content: Dict, resume_data: Dict, website_plan: Dict) -> Dict:
    """Apply default values for missing contact content."""
    
    # Build social links
    social_links = []
    if resume_data.get("github"):
        social_links.append({
            "platform": "github",
            "url": resume_data["github"],
            "icon": "github"
        })
    if resume_data.get("linkedin"):
        social_links.append({
            "platform": "linkedin",
            "url": resume_data["linkedin"],
            "icon": "linkedin"
        })
    if resume_data.get("website"):
        social_links.append({
            "platform": "website",
            "url": resume_data["website"],
            "icon": "globe"
        })
    
    defaults = {
        "title": "Get In Touch",
        "subtitle": "I'd love to hear from you",
        "cta_message": "Whether you have a project in mind or just want to connect, feel free to reach out!",
        "show_form": True,
        "form_fields": ["name", "email", "message"],
        "contact_info": {
            "email": resume_data.get("email"),
            "phone": resume_data.get("phone"),
            "location": None
        },
        "social_links": social_links,
        "availability_status": "Open to opportunities"
    }
    
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
    
    return content
