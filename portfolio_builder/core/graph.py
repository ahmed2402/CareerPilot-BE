"""
LangGraph Workflow Definition for Portfolio Builder.

Builds and compiles the complete multi-agent workflow.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from portfolio_builder.core.state import PortfolioBuilderState, SectionContent
from portfolio_builder.core.routing import (
    should_revalidate,
    check_resume_parsed
)
from portfolio_builder.core.logger import get_logger

logger = get_logger("graph")

# Import all agent nodes
from portfolio_builder.agents.planner import (
    resume_parser_node,
    website_planner_node
)
from portfolio_builder.agents.executors import (
    hero_section_agent,
    about_section_agent,
    skills_section_agent,
    projects_section_agent,
    experience_section_agent,
    contact_section_agent
)
from portfolio_builder.agents.codegen import frontend_generator_node
from portfolio_builder.agents.validator import validator_node
from portfolio_builder.agents.assembler import final_assembler_node


def generate_all_sections_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate content for ALL sections in sequence.
    
    This is a combined node that runs all section generators
    based on sections_to_generate from the planner.
    """
    logger.info("="*60)
    logger.info("GENERATING ALL SECTIONS")
    logger.info("="*60)
    
    sections_to_generate = state.get("sections_to_generate", [])
    resume_data = state.get("resume_parsed", {})
    website_plan = state.get("website_plan", {})
    
    all_sections_content = []
    
    # Map section names to their generator functions
    section_generators = {
        "hero": hero_section_agent,
        "about": about_section_agent,
        "skills": skills_section_agent,
        "projects": projects_section_agent,
        "experience": experience_section_agent,
        "contact": contact_section_agent
    }
    
    for section_name in sections_to_generate:
        section_key = section_name.lower()
        
        if section_key in section_generators:
            logger.info(f"\n--- Processing section: {section_name.upper()} ---")
            
            try:
                # Call the section generator
                generator_fn = section_generators[section_key]
                result = generator_fn(state)
                
                # Extract the section content from the result
                section_content = result.get("sections_content", [])
                if section_content:
                    all_sections_content.extend(section_content)
                    
            except Exception as e:
                logger.error(f"Error generating {section_name}: {e}")
                # Create a fallback section
                all_sections_content.append(SectionContent(
                    section_name=section_key,
                    content={"title": section_name.title(), "subtitle": ""},
                    generated=True,
                    order=len(all_sections_content)
                ))
    
    # Sort by order
    all_sections_content.sort(key=lambda x: x.get("order", 0))
    
    logger.info("="*60)
    logger.info(f"COMPLETED: Generated {len(all_sections_content)} sections total")
    logger.info("="*60)
    
    return {
        "sections_content": all_sections_content,
        "current_node": "section_generator"
    }


def error_handler_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """Handle workflow errors."""
    logger.error("Handling workflow error...")
    
    errors = state.get("errors", [])
    
    return {
        "workflow_status": "failed",
        "errors": errors + ["Workflow failed due to critical error"],
        "current_node": "error_handler"
    }


def build_portfolio_workflow() -> StateGraph:
    """
    Build the complete Portfolio Builder LangGraph workflow.
    
    Simplified workflow structure:
    START → Resume Parser → Website Planner → All Sections Generator →
    Code Generator → Validator ↔ (retry loop) → Assembler → END
    
    Returns:
        Compiled StateGraph workflow
    """
    # Create the state graph
    workflow = StateGraph(PortfolioBuilderState)
    
    # ============ ADD NODES ============
    
    # Planning nodes
    workflow.add_node("resume_parser", resume_parser_node)
    workflow.add_node("website_planner", website_planner_node)
    
    # Combined section generator (runs all sections in sequence)
    workflow.add_node("section_generator", generate_all_sections_node)
    
    # Code generation and validation
    workflow.add_node("code_generator", frontend_generator_node)
    workflow.add_node("validator", validator_node)
    
    # Final assembly
    workflow.add_node("assembler", final_assembler_node)
    
    # Error handler
    workflow.add_node("error_handler", error_handler_node)
    
    # ============ DEFINE EDGES ============
    
    # Entry point
    workflow.set_entry_point("resume_parser")
    
    # Resume parser → conditional check → Website planner or error
    workflow.add_conditional_edges(
        "resume_parser",
        check_resume_parsed,
        {
            "continue": "website_planner",
            "error": "error_handler"
        }
    )
    
    # Website planner → Section generator
    workflow.add_edge("website_planner", "section_generator")
    
    # Section generator → Code generator
    workflow.add_edge("section_generator", "code_generator")
    
    # Code Generator → Validator
    workflow.add_edge("code_generator", "validator")
    
    # Validator → conditional (retry or assemble)
    workflow.add_conditional_edges(
        "validator",
        should_revalidate,
        {
            "regenerate": "code_generator",
            "assemble": "assembler",
            "assemble_with_warnings": "assembler"
        }
    )
    
    # Assembler → END
    workflow.add_edge("assembler", END)
    
    # Error handler → END
    workflow.add_edge("error_handler", END)
    
    return workflow


def compile_workflow():
    """Build and compile the workflow for execution."""
    workflow = build_portfolio_workflow()
    return workflow.compile()


# Create a singleton compiled workflow
_compiled_workflow = None


def get_workflow():
    """Get the compiled workflow (singleton)."""
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = compile_workflow()
    return _compiled_workflow


def reset_workflow():
    """Reset the compiled workflow (useful for testing)."""
    global _compiled_workflow
    _compiled_workflow = None
