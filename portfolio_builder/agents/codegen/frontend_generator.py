"""
Frontend Generator - Orchestrator for code generation.

This module coordinates the three specialized generators:
1. react_generator.py - LLM-based React component generation
2. tailwind_generator.py - LLM colors + hardcoded CSS structure
3. folder_builder.py - 100% hardcoded project structure
"""

from typing import Dict, Any, List

from portfolio_builder.core.state import PortfolioBuilderState, GeneratedCode
from portfolio_builder.core.logger import get_logger

# Import the three specialized generators
from portfolio_builder.agents.codegen.react_generator import (
    generate_react_components,
    generate_app_component,
    generate_main_entry
)
from portfolio_builder.agents.codegen.tailwind_generator import (
    generate_tailwind_styles
)
from portfolio_builder.agents.codegen.folder_builder import (
    generate_project_structure
)

logger = get_logger("frontend_generator")


def frontend_generator_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Orchestrate the complete frontend code generation.
    
    This node coordinates three specialized generators:
    
    1. React Generator (LLM-based):
       - Generates JSX components using LLM with strict prompts
       - Extracts and sanitizes JSX code
       
    2. Tailwind Generator (LLM + hardcoded):
       - LLM decides: colors, responsive patterns
       - Hardcoded: theme tokens, structure
       
    3. Folder Builder (100% hardcoded):
       - Deterministic project structure
       - Config files (package.json, vite.config.js, etc.)
    
    Args:
        state: Current workflow state
        
    Returns:
        Dict with generated_files list
    """
    logger.info("")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║            FRONTEND CODE GENERATION                     ║")
    logger.info("╚" + "="*58 + "╝")
    
    sections_content = state.get("sections_content", [])
    website_plan = state.get("website_plan", {})
    resume_data = state.get("resume_parsed", {})
    
    all_generated_files: List[GeneratedCode] = []
    
    # ============================================================
    # 1. REACT COMPONENTS (LLM-based)
    # ============================================================
    logger.info("\n[1/3] REACT COMPONENT GENERATION")
    
    react_components = generate_react_components(
        sections_content, website_plan, resume_data
    )
    all_generated_files.extend(react_components)
    
    # Generate App.jsx and main.jsx
    app_component = generate_app_component(sections_content, website_plan, resume_data)
    all_generated_files.append(app_component)
    
    main_entry = generate_main_entry()
    all_generated_files.append(main_entry)
    
    # ============================================================
    # 2. TAILWIND/CSS (LLM + hardcoded)
    # ============================================================
    logger.info("\n[2/3] TAILWIND/CSS GENERATION")
    
    tailwind_files = generate_tailwind_styles(website_plan)
    all_generated_files.extend(tailwind_files)
    
    # ============================================================
    # 3. PROJECT STRUCTURE (100% hardcoded)
    # ============================================================
    logger.info("\n[3/3] PROJECT STRUCTURE GENERATION")
    
    structure_files = generate_project_structure(website_plan, resume_data)
    all_generated_files.extend(structure_files)
    
    # ============================================================
    # SUMMARY
    # ============================================================
    logger.info("")
    logger.info("╔" + "="*58 + "╗")
    logger.info(f"║  TOTAL FILES GENERATED: {len(all_generated_files):3d}                            ║")
    logger.info("╠" + "="*58 + "╣")
    logger.info(f"║  React components: {len(react_components):3d} files (LLM-based)              ║")
    logger.info(f"║  Tailwind/CSS:     {len(tailwind_files):3d} files (LLM + hardcoded)         ║")
    logger.info(f"║  Project structure:{len(structure_files):3d} files (100% hardcoded)        ║")
    logger.info("╚" + "="*58 + "╝")
    
    return {
        "generated_files": all_generated_files,
        "current_node": "code_generator"
    }
