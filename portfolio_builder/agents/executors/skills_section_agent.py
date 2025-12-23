"""
Skills Section Agent for Portfolio Builder.

Generates content for the skills/technologies section of the portfolio.
"""

import json
from typing import Dict, Any, List

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.prompts import SKILLS_SECTION_PROMPT
from portfolio_builder.utils.helpers import safe_json_parse
from portfolio_builder.utils.text_cleaner import categorize_skills


def skills_section_agent(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate skills section content.
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with updated sections_content
    """
    print("[SkillsSection] Generating skills section content...")
    
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    skills = resume_data.get("skills", [])
    
    if not skills:
        print("[SkillsSection] No skills found, skipping")
        return {
            "sections_content": [],
            "current_node": "skills_section"
        }
    
    # Use LLM to generate content
    try:
        llm = get_fast_llm(temperature=0.5)
        
        prompt = SKILLS_SECTION_PROMPT.format(
            resume_data=json.dumps(resume_data, indent=2, default=str),
            website_plan=json.dumps(website_plan, indent=2, default=str),
            style=website_plan.get("style", "modern")
        )
        
        response = llm.invoke(prompt)
        content = safe_json_parse(response.content, default={})
        
    except Exception as e:
        print(f"[SkillsSection] ERROR with LLM: {e}")
        content = {}
    
    # Apply defaults
    content = _apply_skills_defaults(content, resume_data, website_plan)
    
    section_content = SectionContent(
        section_name="skills",
        content=content,
        generated=True,
        order=2
    )
    
    print(f"[SkillsSection] Generated content for {len(skills)} skills")
    
    return {
        "sections_content": [section_content],
        "current_node": "skills_section"
    }


def _apply_skills_defaults(content: Dict, resume_data: Dict, website_plan: Dict) -> Dict:
    """Apply default values for missing skills content."""
    skills = resume_data.get("skills", [])
    categorized = categorize_skills(skills)
    
    # Determine display style based on website style
    style = website_plan.get("style", "modern")
    display_styles = {
        "minimal": "tags",
        "modern": "cards",
        "creative": "icons",
        "professional": "bars",
        "bold": "cards"
    }
    
    defaults = {
        "title": "Skills & Technologies",
        "subtitle": "Technologies I work with",
        "categories": _format_categories(categorized),
        "display_style": display_styles.get(style, "cards"),
        "show_proficiency": style in ["professional", "modern"],
        "featured_skills": skills[:6]
    }
    
    for key, value in defaults.items():
        if key not in content or not content[key]:
            content[key] = value
    
    return content


def _format_categories(categorized: Dict[str, List[str]]) -> List[Dict]:
    """Format categorized skills for display."""
    categories = []
    
    # Icon mapping for categories
    icon_map = {
        "Frontend": "layout",
        "Backend": "server",
        "Database": "database",
        "DevOps": "cloud",
        "Languages": "code",
        "Tools": "wrench",
        "Soft Skills": "users",
        "Other": "star"
    }
    
    for category_name, skills in categorized.items():
        if skills:  # Only include non-empty categories
            category = {
                "name": category_name,
                "icon": icon_map.get(category_name, "code"),
                "skills": [
                    {
                        "name": skill,
                        "proficiency": _estimate_proficiency(skill),
                        "icon": _get_skill_icon(skill)
                    }
                    for skill in skills
                ]
            }
            categories.append(category)
    
    return categories


def _estimate_proficiency(skill: str) -> int:
    """Estimate proficiency as a percentage (60-95)."""
    # This is a placeholder - in real applications, this could be user-provided
    # or inferred from resume context
    import hashlib
    # Generate a consistent random-ish number based on skill name
    hash_val = int(hashlib.md5(skill.encode()).hexdigest()[:8], 16)
    return 60 + (hash_val % 36)  # 60-95 range


def _get_skill_icon(skill: str) -> str:
    """Get an icon name for a skill."""
    skill_lower = skill.lower()
    
    icon_map = {
        "react": "react",
        "vue": "vue",
        "angular": "angular",
        "javascript": "javascript",
        "typescript": "typescript",
        "python": "python",
        "java": "java",
        "node": "nodejs",
        "html": "html5",
        "css": "css3",
        "tailwind": "tailwindcss",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "aws": "aws",
        "git": "git",
        "github": "github",
        "figma": "figma",
        "mongodb": "mongodb",
        "postgresql": "postgresql",
        "mysql": "mysql",
        "redis": "redis",
        "graphql": "graphql",
        "next": "nextjs",
    }
    
    for key, icon in icon_map.items():
        if key in skill_lower:
            return icon
    
    return "code"  # Default icon
