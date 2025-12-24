"""
Website Planner Node for Portfolio Builder LangGraph Workflow.

This is the "brain" of the system - it analyzes the resume and user preferences
to create a comprehensive website design plan.
"""

import json
from typing import Dict, Any, List

from portfolio_builder.core.state import PortfolioBuilderState, WebsitePlan
from portfolio_builder.core.llm_config import get_reasoning_llm
from portfolio_builder.core.prompts import WEBSITE_PLANNER_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import safe_json_parse, get_section_order

logger = get_logger("website_planner")


# Default color schemes for different styles
DEFAULT_COLOR_SCHEMES = {
    "minimal": {
        "primary": "#1a1a1a",
        "secondary": "#4a4a4a",
        "accent": "#0066cc",
        "background": "#ffffff",
        "text": "#1a1a1a"
    },
    "modern": {
        "primary": "#6366f1",
        "secondary": "#818cf8",
        "accent": "#22d3ee",
        "background": "#0f172a",
        "text": "#f8fafc"
    },
    "creative": {
        "primary": "#ec4899",
        "secondary": "#8b5cf6",
        "accent": "#fbbf24",
        "background": "#1e1b4b",
        "text": "#ffffff"
    },
    "professional": {
        "primary": "#1e40af",
        "secondary": "#3b82f6",
        "accent": "#059669",
        "background": "#f8fafc",
        "text": "#1e293b"
    },
    "bold": {
        "primary": "#dc2626",
        "secondary": "#f97316",
        "accent": "#fbbf24",
        "background": "#18181b",
        "text": "#fafafa"
    }
}


def website_planner_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Create a comprehensive website design plan based on resume and user preferences.
    
    This node:
    1. Analyzes the parsed resume data
    2. Interprets user preferences from the prompt
    3. Makes design decisions (style, colors, sections, etc.)
    4. Determines which sections to generate
    
    Args:
        state: Current workflow state with resume_parsed and user_prompt
        
    Returns:
        Dict with website_plan and sections_to_generate
    """
    logger.info("Starting website planning...")
    
    resume_data = state.get("resume_parsed", {})
    user_prompt = state.get("user_prompt", "")
    
    if not resume_data:
        logger.warning("No parsed resume data available")
    
    # Step 1: Use LLM to create the website plan
    logger.info("--- LLM: Attempting to get website plan from LLM ---")
    llm_plan = {}
    llm_success = False
    
    try:
        llm = get_reasoning_llm(temperature=0.7)
        
        prompt = WEBSITE_PLANNER_PROMPT.format(
            user_prompt=user_prompt,
            resume_data=json.dumps(resume_data, indent=2, default=str)
        )
        
        response = llm.invoke(prompt)
        llm_plan = safe_json_parse(response.content, default={})
        
        if llm_plan:
            llm_success = True
            logger.info("  [LLM] SUCCESS: LLM returned valid website plan")
            logger.info(f"  [LLM] style: {llm_plan.get('style', 'Not provided')}")
            logger.info(f"  [LLM] color_scheme: {llm_plan.get('color_scheme', 'Not provided')}")
            logger.info(f"  [LLM] sections: {llm_plan.get('sections', 'Not provided')}")
            logger.info(f"  [LLM] font_family: {llm_plan.get('font_family', 'Not provided')}")
            logger.info(f"  [LLM] dark_mode: {llm_plan.get('dark_mode', 'Not provided')}")
            logger.info(f"  [LLM] use_animations: {llm_plan.get('use_animations', 'Not provided')}")
        else:
            logger.warning("  [LLM] WARNING: LLM returned empty plan, will use defaults")
        
    except Exception as e:
        logger.error(f"  [LLM] ERROR: LLM planning failed: {e}")
        logger.warning("  [LLM] Will use default configuration")
    
    # Step 2: Build the website plan, logging source of each value
    logger.info("--- BUILDING PLAN: Determining final values ---")
    
    # Style
    if llm_plan.get("style"):
        style = llm_plan["style"]
        logger.info(f"  style: '{style}' <- LLM")
    else:
        style = _infer_style_from_prompt(user_prompt)
        logger.info(f"  style: '{style}' <- DEFAULT (inferred from prompt)")
    
    # Color scheme
    if llm_plan.get("color_scheme"):
        color_scheme = llm_plan["color_scheme"]
        logger.info(f"  color_scheme: {color_scheme} <- LLM")
    else:
        color_scheme = DEFAULT_COLOR_SCHEMES.get(style, DEFAULT_COLOR_SCHEMES["creative"])
        logger.info(f"  color_scheme: {color_scheme} <- DEFAULT (for {style} style)")
    
    # Sections
    determined_sections = _determine_sections(resume_data, llm_plan.get("sections", []))
    if llm_plan.get("sections"):
        logger.info(f"  sections: {determined_sections} <- LLM + DATA AVAILABILITY")
    else:
        logger.info(f"  sections: {determined_sections} <- DEFAULT (based on resume data)")
    
    # Layout
    if llm_plan.get("layout"):
        layout = llm_plan["layout"]
        logger.info(f"  layout: '{layout}' <- LLM")
    else:
        layout = "single_page"
        logger.info(f"  layout: '{layout}' <- DEFAULT")
    
    # Animations
    if "use_animations" in llm_plan:
        use_animations = llm_plan["use_animations"]
        logger.info(f"  use_animations: {use_animations} <- LLM")
    else:
        use_animations = _should_use_animations(user_prompt, style)
        logger.info(f"  use_animations: {use_animations} <- DEFAULT (based on style)")
    
    # Font family
    if llm_plan.get("font_family"):
        font_family = llm_plan["font_family"]
        logger.info(f"  font_family: '{font_family}' <- LLM")
    else:
        font_family = "Inter"
        logger.info(f"  font_family: '{font_family}' <- DEFAULT")
    
    # Dark mode
    if "dark_mode" in llm_plan:
        dark_mode = llm_plan["dark_mode"]
        logger.info(f"  dark_mode: {dark_mode} <- LLM")
    else:
        dark_mode = style in ["modern", "creative", "bold"]
        logger.info(f"  dark_mode: {dark_mode} <- DEFAULT (based on style)")
    
    # Navigation style
    if llm_plan.get("navigation_style"):
        navigation_style = llm_plan["navigation_style"]
        logger.info(f"  navigation_style: '{navigation_style}' <- LLM")
    else:
        navigation_style = "sticky"
        logger.info(f"  navigation_style: '{navigation_style}' <- DEFAULT")
    
    # Build the final plan
    website_plan = WebsitePlan(
        style=style,
        color_scheme=color_scheme,
        sections=determined_sections,
        layout=layout,
        use_animations=use_animations,
        animation_library="framer-motion" if use_animations else None,
        tech_stack=["react", "tailwind"] + (["framer-motion"] if use_animations else []),
        font_family=font_family,
        dark_mode=dark_mode,
        navigation_style=navigation_style
    )
    
    # Step 3: Determine which sections to generate
    sections_to_generate = get_section_order(website_plan["sections"])
    
    logger.info("--- RESULT ---")
    logger.info(f"  Final style: {website_plan['style']}")
    logger.info(f"  Final primary color: {website_plan['color_scheme'].get('primary')}")
    logger.info(f"  Final sections: {sections_to_generate}")
    logger.info(f"  Plan source: {'Primarily LLM' if llm_success else 'Primarily DEFAULTS'}")
    
    return {
        "website_plan": website_plan,
        "sections_to_generate": sections_to_generate,
        "current_node": "website_planner"
    }


def _infer_style_from_prompt(user_prompt: str) -> str:
    """Infer website style from user prompt keywords."""
    prompt_lower = user_prompt.lower() if user_prompt else ""
    
    style_keywords = {
        "minimal": ["minimal", "simple", "clean", "minimalist", "basic"],
        "modern": ["modern", "sleek", "tech", "startup", "contemporary"],
        "creative": ["creative", "artistic", "unique", "bold colors", "vibrant"],
        "professional": ["professional", "corporate", "formal", "business", "traditional"],
        "bold": ["bold", "standout", "eye-catching", "striking", "dramatic"]
    }
    
    for style, keywords in style_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return style
    
    return "modern"  # Default


def _should_use_animations(user_prompt: str, style: str) -> bool:
    """Determine if animations should be used."""
    prompt_lower = user_prompt.lower() if user_prompt else ""
    
    # Check for explicit preferences
    if any(word in prompt_lower for word in ["no animation", "simple", "fast", "static"]):
        return False
    
    if any(word in prompt_lower for word in ["animated", "animation", "dynamic", "interactive"]):
        return True
    
    # Default based on style
    return style in ["modern", "creative", "bold"]


def _determine_sections(resume_data: Dict, llm_sections: List[str]) -> List[str]:
    """
    Determine which sections to include based on available data.
    
    Always includes: hero, about, contact
    Conditionally includes: skills, projects, experience, education, certifications
    """
    # Always required sections
    sections = ["hero", "about", "contact"]
    
    # Check for data availability
    if resume_data.get("skills"):
        sections.append("skills")
    
    if resume_data.get("projects"):
        sections.append("projects")
    
    if resume_data.get("experience"):
        sections.append("experience")
    
    # These are optional even if data exists
    if resume_data.get("education") and "education" in llm_sections:
        sections.append("education")
    
    if resume_data.get("certifications") and "certifications" in llm_sections:
        sections.append("certifications")
    
    # Add any LLM-suggested sections that we have data for
    for section in llm_sections:
        if section not in sections:
            # Check if we have data for this section
            if section == "skills" and resume_data.get("skills"):
                sections.append("skills")
            elif section == "projects" and resume_data.get("projects"):
                sections.append("projects")
            elif section == "experience" and resume_data.get("experience"):
                sections.append("experience")
            elif section == "education" and resume_data.get("education"):
                sections.append("education")
    
    return sections
