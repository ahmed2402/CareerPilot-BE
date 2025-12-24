"""
Resume Parser Node for Portfolio Builder LangGraph Workflow.

This node extracts structured data from raw resume text using an LLM.
"""

import json
from typing import Dict, Any

from portfolio_builder.core.state import PortfolioBuilderState, ResumeData
from portfolio_builder.core.llm_config import get_reasoning_llm
from portfolio_builder.core.prompts import RESUME_PARSER_PROMPT
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.text_cleaner import (
    clean_resume_text, 
    extract_urls, 
    extract_phone,
    normalize_skills,
    extract_name
)
from portfolio_builder.utils.helpers import safe_json_parse

logger = get_logger("resume_parser")


def resume_parser_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Parse raw resume text into structured ResumeData.
    
    This node:
    1. Cleans the raw resume text
    2. Uses an LLM to extract structured information
    3. Validates and enhances the extracted data
    4. Returns the parsed resume data
    
    Args:
        state: Current workflow state with resume_text
        
    Returns:
        Dict with resume_parsed and parsing_confidence
    """
    logger.info("Starting resume parsing...")
    
    resume_text = state.get("resume_text", "")
    
    if not resume_text:
        logger.error("No resume text provided")
        return {
            "resume_parsed": ResumeData(),
            "parsing_confidence": 0.0,
            "errors": state.get("errors", []) + ["No resume text provided"],
            "current_node": "resume_parser"
        }
    
    # Step 1: Clean the resume text
    cleaned_text = clean_resume_text(resume_text)
    logger.info(f"Cleaned text length: {len(cleaned_text)} chars")
    
    # Step 2: Extract URLs and contact info directly using UTILITY FUNCTIONS (as backup)
    logger.info("--- UTILITY FUNCTIONS: Extracting contact info as backup ---")
    extracted_urls = extract_urls(cleaned_text)
    extracted_phone = extract_phone(cleaned_text)
    extracted_name = extract_name(cleaned_text)
    logger.info(f"  [UTILITY] Extracted name: {extracted_name or 'Not found'}")
    logger.info(f"  [UTILITY] Extracted email: {extracted_urls.get('email') or 'Not found'}")
    logger.info(f"  [UTILITY] Extracted phone: {extracted_phone or 'Not found'}")
    logger.info(f"  [UTILITY] Extracted github: {extracted_urls.get('github') or 'Not found'}")
    logger.info(f"  [UTILITY] Extracted linkedin: {extracted_urls.get('linkedin') or 'Not found'}")
    
    # Step 3: Use LLM to extract structured data
    logger.info("--- LLM: Attempting to parse resume with LLM ---")
    llm_result = {}
    llm_success = False
    
    try:
        llm = get_reasoning_llm(temperature=0.1)  # Low temperature for accuracy
        
        prompt = RESUME_PARSER_PROMPT.format(resume_text=cleaned_text)
        response = llm.invoke(prompt)
        
        llm_result = safe_json_parse(response.content, default={})
        
        if llm_result:
            llm_success = True
            logger.info("  [LLM] SUCCESS: LLM returned valid parsed data")
            logger.info(f"  [LLM] Name: {llm_result.get('name', 'Not found')}")
            logger.info(f"  [LLM] Skills count: {len(llm_result.get('skills', []))}")
            logger.info(f"  [LLM] Projects count: {len(llm_result.get('projects', []))}")
            logger.info(f"  [LLM] Experience count: {len(llm_result.get('experience', []))}")
        else:
            logger.warning("  [LLM] WARNING: LLM returned empty result, will use utility fallbacks")
        
    except Exception as e:
        logger.error(f"  [LLM] ERROR: LLM parsing failed: {e}")
        logger.warning("  [LLM] Will use utility function fallbacks")
    
    # Step 4: Build the final ResumeData, merging LLM results with direct extraction
    logger.info("--- MERGING: Building final resume data ---")
    
    # For each field, log whether we're using LLM or utility function result
    final_name = llm_result.get("name") or extracted_name or "Unknown"
    logger.info(f"  name: '{final_name}' <- {'LLM' if llm_result.get('name') else ('UTILITY' if extracted_name else 'DEFAULT')}")
    
    final_email = llm_result.get("email") or extracted_urls.get("email")
    logger.info(f"  email: '{final_email}' <- {'LLM' if llm_result.get('email') else 'UTILITY'}")
    
    final_phone = llm_result.get("phone") or extracted_phone
    logger.info(f"  phone: '{final_phone}' <- {'LLM' if llm_result.get('phone') else 'UTILITY'}")
    
    final_github = llm_result.get("github") or extracted_urls.get("github")
    logger.info(f"  github: '{final_github}' <- {'LLM' if llm_result.get('github') else 'UTILITY'}")
    
    final_linkedin = llm_result.get("linkedin") or extracted_urls.get("linkedin")
    logger.info(f"  linkedin: '{final_linkedin}' <- {'LLM' if llm_result.get('linkedin') else 'UTILITY'}")
    
    skills_source = "LLM" if llm_result.get("skills") else "EMPTY"
    logger.info(f"  skills: {len(llm_result.get('skills', []))} items <- {skills_source}")
    
    projects_source = "LLM" if llm_result.get("projects") else "EMPTY"
    logger.info(f"  projects: {len(llm_result.get('projects', []))} items <- {projects_source}")
    
    experience_source = "LLM" if llm_result.get("experience") else "EMPTY"
    logger.info(f"  experience: {len(llm_result.get('experience', []))} items <- {experience_source}")
    
    resume_data = ResumeData(
        name=final_name,
        email=final_email,
        phone=final_phone,
        linkedin=final_linkedin,
        github=final_github,
        website=llm_result.get("website") or extracted_urls.get("website"),
        summary=llm_result.get("summary"),
        skills=normalize_skills(llm_result.get("skills", [])),
        projects=llm_result.get("projects", []),
        experience=llm_result.get("experience", []),
        education=llm_result.get("education", []),
        certifications=llm_result.get("certifications", []),
        languages=llm_result.get("languages", []),
        interests=llm_result.get("interests", [])
    )
    
    # Step 5: Calculate parsing confidence
    confidence = _calculate_parsing_confidence(resume_data)
    
    logger.info("--- RESULT ---")
    logger.info(f"  Parsed resume for: {resume_data.get('name', 'Unknown')}")
    logger.info(f"  Total skills: {len(resume_data.get('skills', []))}")
    logger.info(f"  Total projects: {len(resume_data.get('projects', []))}")
    logger.info(f"  Total experiences: {len(resume_data.get('experience', []))}")
    logger.info(f"  Confidence: {confidence:.2f}")
    logger.info(f"  Data source: {'Primarily LLM' if llm_success else 'Primarily UTILITY FUNCTIONS'}")
    
    return {
        "resume_parsed": resume_data,
        "parsing_confidence": confidence,
        "current_node": "resume_parser"
    }


def _calculate_parsing_confidence(resume_data: ResumeData) -> float:
    """
    Calculate confidence score based on extracted data completeness.
    
    Returns a score from 0.0 to 1.0.
    """
    score = 0.0
    max_score = 10.0
    
    # Name (required)
    if resume_data.get("name") and resume_data["name"] != "Unknown":
        score += 1.5
    
    # Contact info
    if resume_data.get("email"):
        score += 1.0
    if resume_data.get("phone"):
        score += 0.5
    if resume_data.get("linkedin") or resume_data.get("github"):
        score += 0.5
    
    # Skills
    skills = resume_data.get("skills", [])
    if len(skills) >= 5:
        score += 2.0
    elif len(skills) >= 2:
        score += 1.0
    elif len(skills) >= 1:
        score += 0.5
    
    # Projects
    projects = resume_data.get("projects", [])
    if len(projects) >= 3:
        score += 2.0
    elif len(projects) >= 1:
        score += 1.0
    
    # Experience
    experience = resume_data.get("experience", [])
    if len(experience) >= 2:
        score += 2.0
    elif len(experience) >= 1:
        score += 1.0
    
    # Education
    if resume_data.get("education"):
        score += 0.5
    
    return min(score / max_score, 1.0)
