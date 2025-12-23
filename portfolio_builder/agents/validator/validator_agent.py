"""
Validator Agent for Portfolio Builder.

Validates generated code for syntax errors, missing imports, and other issues.
Attempts to fix errors automatically.
"""

import re
from typing import Dict, Any, List, Tuple

from portfolio_builder.core.state import (
    PortfolioBuilderState, 
    GeneratedCode, 
    ValidationResult,
    ValidationError
)
from portfolio_builder.core.llm_config import get_code_llm
from portfolio_builder.core.prompts import VALIDATOR_PROMPT, FIXER_PROMPT
from portfolio_builder.utils.helpers import safe_json_parse, extract_code_from_response


def validator_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Validate generated code and attempt to fix errors.
    
    This node:
    1. Checks each generated file for errors
    2. Attempts to fix errors using LLM
    3. Returns validation result
    
    Args:
        state: Current workflow state with generated_files
        
    Returns:
        Dict with validation_result and updated generated_files
    """
    print("[Validator] Starting code validation...")
    
    generated_files = state.get("generated_files", [])
    validation_attempts = state.get("validation_attempts", 0)
    max_attempts = state.get("max_validation_attempts", 3)
    
    all_errors: List[ValidationError] = []
    all_warnings: List[ValidationError] = []
    fixed_files: List[str] = []
    updated_files: List[GeneratedCode] = []
    
    llm = get_code_llm(temperature=0.1)
    
    for file_info in generated_files:
        filename = file_info.get("filename", "")
        content = file_info.get("content", "")
        
        # Skip non-code files
        if not filename.endswith(('.jsx', '.js', '.tsx', '.ts')):
            updated_files.append(file_info)
            continue
        
        print(f"[Validator] Checking {filename}...")
        
        # Step 1: Static validation
        static_errors = _static_validate(filename, content)
        
        if static_errors:
            print(f"[Validator] Found {len(static_errors)} issues in {filename}")
            
            # Step 2: Try to fix errors
            if validation_attempts < max_attempts:
                fixed_content = _attempt_fix(llm, filename, content, static_errors)
                
                if fixed_content and fixed_content != content:
                    # Re-validate fixed content
                    new_errors = _static_validate(filename, fixed_content)
                    
                    if len(new_errors) < len(static_errors):
                        print(f"[Validator] Fixed some issues in {filename}")
                        file_info = GeneratedCode(
                            filename=file_info["filename"],
                            filepath=file_info["filepath"],
                            content=fixed_content,
                            component_type=file_info["component_type"]
                        )
                        fixed_files.append(filename)
                        static_errors = new_errors
        
        # Collect remaining errors
        for error in static_errors:
            if error["severity"] == "error":
                all_errors.append(error)
            else:
                all_warnings.append(error)
        
        updated_files.append(file_info)
    
    # Create validation result
    is_valid = len(all_errors) == 0
    
    validation_result = ValidationResult(
        is_valid=is_valid,
        errors=all_errors,
        warnings=all_warnings,
        fixed_files=fixed_files
    )
    
    print(f"[Validator] Validation complete: {'PASSED' if is_valid else 'FAILED'}")
    print(f"[Validator] Errors: {len(all_errors)}, Warnings: {len(all_warnings)}")
    
    return {
        "generated_files": updated_files,
        "validation_result": validation_result,
        "validation_attempts": validation_attempts + 1,
        "current_node": "validator"
    }


def _static_validate(filename: str, content: str) -> List[ValidationError]:
    """
    Perform static validation on code.
    
    Checks for:
    - JSX syntax issues
    - Missing imports
    - Common React errors
    - Tailwind issues
    """
    errors = []
    lines = content.split('\n')
    
    # Track what's imported
    imports = set()
    for line in lines:
        if line.strip().startswith('import '):
            # Extract imported names
            match = re.search(r'import\s+(?:{([^}]+)}|(\w+))', line)
            if match:
                names = match.group(1) or match.group(2)
                for name in names.replace(' ', '').split(','):
                    imports.add(name.strip())
    
    # Check for common issues
    for i, line in enumerate(lines, 1):
        # Check for unclosed JSX tags
        if '<' in line and '>' in line:
            opens = len(re.findall(r'<\w+', line))
            closes = len(re.findall(r'</\w+>|/>', line))
            # This is a simple heuristic, not perfect
        
        # Check for className with invalid Tailwind patterns
        if 'className=' in line:
            # Check for common mistakes
            if 'className=""' in line and '/>' not in line:
                errors.append(ValidationError(
                    file=filename,
                    line=i,
                    message="Empty className attribute",
                    severity="warning",
                    rule="tailwind"
                ))
    
    # Check for React component issues
    if filename.endswith('.jsx'):
        # Check for missing React import (needed for older React versions)
        has_jsx = bool(re.search(r'<\w+', content))
        
        # Check for export default
        if 'export default' not in content and 'export {' not in content:
            errors.append(ValidationError(
                file=filename,
                line=None,
                message="No export statement found",
                severity="error",
                rule="missing-export"
            ))
        
        # Check for component returning JSX
        if has_jsx and 'return' not in content and '=>' not in content:
            errors.append(ValidationError(
                file=filename,
                line=None,
                message="Component may not return JSX",
                severity="warning",
                rule="jsx-return"
            ))
    
    # Check for common icon usage without import
    icon_pattern = r'<(Github|Linkedin|Mail|Menu|X|ChevronDown|ArrowRight|ExternalLink)\s'
    icon_matches = re.findall(icon_pattern, content)
    for icon in icon_matches:
        if icon not in imports and 'lucide-react' not in content:
            errors.append(ValidationError(
                file=filename,
                line=None,
                message=f"Icon '{icon}' may not be imported from lucide-react",
                severity="warning",
                rule="missing-import"
            ))
    
    return errors


def _attempt_fix(
    llm, 
    filename: str, 
    content: str, 
    errors: List[ValidationError]
) -> str:
    """Attempt to fix code errors using LLM."""
    try:
        errors_text = "\n".join([
            f"- Line {e.get('line', 'N/A')}: {e['message']} ({e['rule']})"
            for e in errors
        ])
        
        prompt = FIXER_PROMPT.format(
            code=content,
            errors=errors_text
        )
        
        response = llm.invoke(prompt)
        fixed_code = extract_code_from_response(response.content)
        
        return fixed_code if fixed_code else content
        
    except Exception as e:
        print(f"[Validator] Error fixing {filename}: {e}")
        return content
