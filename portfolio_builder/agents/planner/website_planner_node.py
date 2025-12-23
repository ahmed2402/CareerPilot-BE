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
from portfolio_builder.utils.helpers import safe_json_parse, get_section_order


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
    print("[WebsitePlanner] Starting website planning...")
    
    resume_data = state.get("resume_parsed", {})
    user_prompt = state.get("user_prompt", "")
    
    if not resume_data:
        print("[WebsitePlanner] WARNING: No parsed resume data")
    
    # Step 1: Use LLM to create the website plan
    try:
        llm = get_reasoning_llm(temperature=0.7)
        
        prompt = WEBSITE_PLANNER_PROMPT.format(
            user_prompt=user_prompt or "Create a modern professional portfolio website",
            resume_data=json.dumps(resume_data, indent=2, default=str)
        )
        
        response = llm.invoke(prompt)
        llm_plan = safe_json_parse(response.content, default={})
        
        if not llm_plan:
            print("[WebsitePlanner] WARNING: LLM returned empty plan, using defaults")
            llm_plan = {}
        
    except Exception as e:
        print(f"[WebsitePlanner] ERROR with LLM: {e}")
        llm_plan = {}
    
    # Step 2: Build the website plan with defaults
    style = llm_plan.get("style", _infer_style_from_prompt(user_prompt))
    
    website_plan = WebsitePlan(
        style=style,
        color_scheme=llm_plan.get("color_scheme", DEFAULT_COLOR_SCHEMES.get(style, DEFAULT_COLOR_SCHEMES["modern"])),
        sections=_determine_sections(resume_data, llm_plan.get("sections", [])),
        layout=llm_plan.get("layout", "single_page"),
        use_animations=llm_plan.get("use_animations", _should_use_animations(user_prompt, style)),
        animation_library="framer-motion" if llm_plan.get("use_animations", True) else None,
        tech_stack=["react", "tailwind"] + (["framer-motion"] if llm_plan.get("use_animations", True) else []),
        font_family=llm_plan.get("font_family", "Inter"),
        dark_mode=llm_plan.get("dark_mode", style in ["modern", "creative", "bold"]),
        navigation_style=llm_plan.get("navigation_style", "sticky")
    )
    
    # Step 3: Determine which sections to generate
    sections_to_generate = get_section_order(website_plan["sections"])
    
    print(f"[WebsitePlanner] Style: {website_plan['style']}")
    print(f"[WebsitePlanner] Sections: {sections_to_generate}")
    print(f"[WebsitePlanner] Animations: {website_plan['use_animations']}")
    print(f"[WebsitePlanner] Dark mode: {website_plan['dark_mode']}")
    
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
