"""
Validator Agent for Portfolio Builder.

Validates generated code with self-healing capabilities.
- Checks for syntax errors, missing imports, React rules
- Attempts LLM-based fixes with retry loop (max 3 retries)
- Returns validation result
"""

import re
from typing import Dict, Any, List, Tuple, Optional

from portfolio_builder.core.state import (
    PortfolioBuilderState, 
    GeneratedCode, 
    ValidationResult,
    ValidationError
)
from portfolio_builder.core.llm_config import get_code_llm
from portfolio_builder.core.logger import get_logger

logger = get_logger("validator")

# Maximum retry attempts for self-healing
MAX_RETRIES = 3

# LLM prompt for fixing code
FIX_PROMPT = """Fix the following React/JSX code errors:

ERRORS FOUND:
{errors}

ORIGINAL CODE:
```jsx
{code}
```

RULES:
1. Fix ALL the errors listed above
2. Keep the component structure intact
3. Ensure all imports are correct
4. Ensure proper JSX syntax
5. Return ONLY the fixed code, no explanations

Return the complete fixed code starting with 'import' and ending with 'export default'.
"""


def validator_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Validate generated code with self-healing retry loop.
    
    This node implements an AGENTIC retry loop:
    1. Validates each file for errors
    2. If errors found, attempts LLM-based fix
    3. Re-validates fixed code
    4. Repeats up to MAX_RETRIES times
    
    Args:
        state: Current workflow state with generated_files
        
    Returns:
        Dict with validation_result and updated generated_files
    """
    logger.info("="*60)
    logger.info("CODE VALIDATION (Self-Healing)")
    logger.info("="*60)
    
    generated_files = state.get("generated_files", [])
    validation_attempts = state.get("validation_attempts", 0)
    
    logger.info(f"  Validation attempt: {validation_attempts + 1}")
    logger.info(f"  Max retries: {MAX_RETRIES}")
    logger.info(f"  Files to validate: {len(generated_files)}")
    
    all_errors: List[ValidationError] = []
    all_warnings: List[ValidationError] = []
    fixed_files: List[str] = []
    updated_files: List[GeneratedCode] = []
    
    # Initialize LLM for fixes
    try:
        llm = get_code_llm(temperature=0.1)
        llm_available = True
        logger.info("  [LLM] Available for self-healing")
    except Exception as e:
        logger.warning(f"  [LLM] Not available: {e}")
        llm = None
        llm_available = False
    
    for file_info in generated_files:
        filename = file_info.get("filename", "")
        content = file_info.get("content", "")
        
        # Skip non-code files
        if not filename.endswith(('.jsx', '.js', '.tsx', '.ts')):
            updated_files.append(file_info)
            continue
        
        logger.info(f"\n--- Validating: {filename} ---")
        
        # VALIDATION + SELF-HEALING LOOP
        current_content = content
        file_errors = []
        fixed = False
        
        for retry in range(MAX_RETRIES):
            # Step 1: Static validation [HARDCODED rules]
            logger.info(f"  [HARDCODED] Running static validation (attempt {retry + 1}/{MAX_RETRIES})")
            static_errors = _static_validate(filename, current_content)
            
            if not static_errors:
                logger.info(f"  ✓ No errors found")
                break
            
            # Log errors
            error_count = len([e for e in static_errors if e["severity"] == "error"])
            warning_count = len([e for e in static_errors if e["severity"] == "warning"])
            logger.info(f"  Found: {error_count} errors, {warning_count} warnings")
            
            # Step 2: Attempt self-healing with LLM
            if llm_available and error_count > 0:
                logger.info(f"  [LLM] Attempting self-healing fix...")
                
                fixed_content = _self_heal_with_llm(llm, filename, current_content, static_errors)
                
                if fixed_content and fixed_content != current_content:
                    # Verify the fix worked
                    new_errors = _static_validate(filename, fixed_content)
                    new_error_count = len([e for e in new_errors if e["severity"] == "error"])
                    
                    if new_error_count < error_count:
                        logger.info(f"  [LLM] SUCCESS: Reduced errors from {error_count} to {new_error_count}")
                        current_content = fixed_content
                        static_errors = new_errors
                        fixed = True
                        
                        if new_error_count == 0:
                            logger.info(f"  ✓ All errors fixed!")
                            break
                    else:
                        logger.warning(f"  [LLM] Fix did not reduce errors, keeping original")
                else:
                    logger.warning(f"  [LLM] No fix generated")
            else:
                # No LLM, try hardcoded fixes
                logger.info(f"  [HARDCODED] Attempting basic fixes...")
                fixed_content = _apply_hardcoded_fixes(filename, current_content, static_errors)
                
                if fixed_content != current_content:
                    current_content = fixed_content
                    fixed = True
                    logger.info(f"  [HARDCODED] Applied basic fixes")
            
            file_errors = static_errors
        
        # Collect final errors/warnings
        for error in file_errors:
            if error["severity"] == "error":
                all_errors.append(error)
            else:
                all_warnings.append(error)
        
        # Update file with fixed content
        if fixed:
            file_info = GeneratedCode(
                filename=file_info["filename"],
                filepath=file_info["filepath"],
                content=current_content,
                component_type=file_info["component_type"]
            )
            fixed_files.append(filename)
        
        updated_files.append(file_info)
    
    # Create validation result
    is_valid = len(all_errors) == 0
    
    validation_result = ValidationResult(
        is_valid=is_valid,
        errors=all_errors,
        warnings=all_warnings,
        fixed_files=fixed_files
    )
    
    logger.info("")
    logger.info("="*60)
    logger.info(f"VALIDATION RESULT: {'✓ PASSED' if is_valid else '✗ FAILED'}")
    logger.info(f"  Errors: {len(all_errors)}")
    logger.info(f"  Warnings: {len(all_warnings)}")
    logger.info(f"  Files fixed: {len(fixed_files)}")
    logger.info("="*60)
    
    return {
        "generated_files": updated_files,
        "validation_result": validation_result,
        "validation_attempts": validation_attempts + 1,
        "current_node": "validator"
    }


def _static_validate(filename: str, content: str) -> List[ValidationError]:
    """
    Perform static validation on code [HARDCODED rules].
    
    Checks for:
    - JSX syntax issues
    - Missing imports
    - Common React errors
    - Missing exports
    """
    errors = []
    lines = content.split('\n')
    
    # Track what's imported
    imports = set()
    for line in lines:
        if line.strip().startswith('import '):
            match = re.search(r'import\s+(?:{([^}]+)}|(\w+))', line)
            if match:
                names = match.group(1) or match.group(2)
                for name in names.replace(' ', '').split(','):
                    imports.add(name.strip())
    
    # === REACT COMPONENT CHECKS ===
    if filename.endswith('.jsx') or filename.endswith('.tsx'):
        
        # Check: Missing export
        if 'export default' not in content and 'export {' not in content:
            # Skip for entry point files
            if 'main.jsx' not in filename:
                errors.append(ValidationError(
                    file=filename,
                    line=None,
                    message="Missing export statement",
                    severity="error",
                    rule="missing-export"
                ))
        
        # Check: Component must have return
        has_jsx = bool(re.search(r'<\w+', content))
        has_return = 'return' in content or '=>' in content
        if has_jsx and not has_return:
            errors.append(ValidationError(
                file=filename,
                line=None,
                message="Component doesn't return JSX",
                severity="error",
                rule="no-return"
            ))
        
        # Check: React import (optional but good practice)
        if has_jsx and 'React' not in imports and 'import React' not in content:
            # React 17+ doesn't require React import for JSX
            pass  # Not an error in modern React
        
        # Check: Lucide icons imported
        icon_pattern = r'<(Github|Linkedin|Mail|Menu|X|ChevronDown|ArrowDown|ArrowRight|ExternalLink|User|Send)\s'
        icon_matches = set(re.findall(icon_pattern, content))
        for icon in icon_matches:
            if icon not in imports:
                errors.append(ValidationError(
                    file=filename,
                    line=None,
                    message=f"Icon '{icon}' used but not imported from lucide-react",
                    severity="error",
                    rule="missing-icon-import"
                ))
        
        # Check: Unclosed JSX tags (basic check)
        open_tags = len(re.findall(r'<\w+[^/>]*>', content))
        close_tags = len(re.findall(r'</\w+>', content))
        self_close = len(re.findall(r'/>', content))
        
        if open_tags > close_tags + self_close + 5:  # Allow some tolerance
            errors.append(ValidationError(
                file=filename,
                line=None,
                message="Possible unclosed JSX tags",
                severity="warning",
                rule="unclosed-tag"
            ))
        
        # Check: Empty className
        for i, line in enumerate(lines, 1):
            if 'className=""' in line:
                errors.append(ValidationError(
                    file=filename,
                    line=i,
                    message="Empty className attribute",
                    severity="warning",
                    rule="empty-classname"
                ))
            
            # Check: Unescaped quotes in JSX
            if "style={'" in line or "style=\"" in line:
                errors.append(ValidationError(
                    file=filename,
                    line=i,
                    message="Style prop should use object syntax",
                    severity="warning",
                    rule="style-object"
                ))
    
    return errors


def _self_heal_with_llm(
    llm,
    filename: str,
    content: str,
    errors: List[ValidationError]
) -> Optional[str]:
    """
    Attempt to fix code using LLM [LLM-based self-healing].
    """
    try:
        errors_text = "\n".join([
            f"- {e['message']} (rule: {e['rule']}, line: {e.get('line', 'N/A')})"
            for e in errors if e['severity'] == 'error'
        ])
        
        if not errors_text:
            return None
        
        prompt = FIX_PROMPT.format(
            code=content,
            errors=errors_text
        )
        
        response = llm.invoke(prompt)
        fixed_code = _extract_code(response.content)
        
        return fixed_code if fixed_code else None
        
    except Exception as e:
        logger.error(f"  [LLM] Error during self-healing: {e}")
        return None


def _extract_code(response: str) -> Optional[str]:
    """Extract code from LLM response."""
    patterns = [
        r'```jsx\s*(.*?)\s*```',
        r'```javascript\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    if response.strip().startswith('import'):
        return response.strip()
    
    return None


def _apply_hardcoded_fixes(
    filename: str,
    content: str,
    errors: List[ValidationError]
) -> str:
    """
    Apply hardcoded fixes for common issues [HARDCODED].
    """
    fixed_content = content
    
    for error in errors:
        rule = error.get("rule", "")
        
        # Fix: Missing export
        if rule == "missing-export":
            # Try to find component name and add export
            match = re.search(r'const\s+(\w+)\s*=', content)
            if match:
                component_name = match.group(1)
                if f'export default {component_name}' not in content:
                    fixed_content += f"\n\nexport default {component_name};\n"
                    logger.info(f"    [HARDCODED] Added export default {component_name}")
        
        # Fix: Missing icon import
        if rule == "missing-icon-import":
            icon_name = error["message"].split("'")[1]
            # Check if lucide-react import exists
            if 'lucide-react' in content:
                # Add to existing import
                fixed_content = re.sub(
                    r"import\s*{\s*([^}]+)\s*}\s*from\s*['\"]lucide-react['\"]",
                    lambda m: f"import {{ {m.group(1)}, {icon_name} }} from 'lucide-react'",
                    fixed_content
                )
                logger.info(f"    [HARDCODED] Added {icon_name} to lucide-react import")
            else:
                # Add new import at top
                fixed_content = f"import {{ {icon_name} }} from 'lucide-react';\n" + fixed_content
                logger.info(f"    [HARDCODED] Added lucide-react import for {icon_name}")
    
    return fixed_content
