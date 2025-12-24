"""
Tailwind/CSS Generator - LLM-based for custom utilities + hardcoded structure.

LLM decides: custom CSS utilities, animations, responsive patterns
Hardcoded: base CSS structure, theme tokens, font imports
"""

from typing import Dict, Any, List

from portfolio_builder.core.state import GeneratedCode
from portfolio_builder.core.llm_config import get_fast_llm
from portfolio_builder.core.logger import get_logger

logger = get_logger("tailwind_generator")


# ============================================================
# HARDCODED: Theme Tokens (never from LLM)
# ============================================================
FONT_IMPORTS = {
    "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap",
    "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap",
    "Open Sans": "https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap",
    "Montserrat": "https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap",
}

# HARDCODED: Base CSS structure (never changes)
BASE_CSS_STRUCTURE = """@tailwind base;
@tailwind components;
@tailwind utilities;

{font_import}

:root {{
  --color-primary: {primary};
  --color-secondary: {secondary};
  --color-accent: {accent};
  --color-background: {background};
  --color-text: {text};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

html {{
  scroll-behavior: smooth;
}}

body {{
  font-family: '{font_family}', sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.6;
}}

/* Smooth scrolling offset for fixed nav */
section {{
  scroll-margin-top: 64px;
}}

{custom_utilities}
"""

# HARDCODED: Tailwind config structure
TAILWIND_CONFIG_STRUCTURE = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '%s',
        secondary: '%s',
        accent: '%s',
        background: '%s',
        text: '%s',
      },
      fontFamily: {
        sans: ['%s', 'sans-serif'],
      },
      %s
    },
  },
  plugins: [],
}
"""

# LLM prompt for generating custom CSS utilities
CUSTOM_UTILITIES_PROMPT = """Generate custom CSS utilities for a {style} portfolio website.

COLOR SCHEME:
- Primary: {primary}
- Secondary: {secondary}
- Accent: {accent}
- Background: {background}
- Text: {text}

REQUIREMENTS:
- Style: {style}
- Use animations: {use_animations}
- Create utilities that match the style (e.g., glassmorphism for modern, gradients for creative)

Generate CSS utilities ONLY. No explanations. Include:
1. Animation keyframes (if animations enabled)
2. Style-specific effects (glass, gradients, shadows)
3. Hover states
4. Custom transition utilities

Return ONLY valid CSS code starting with /* and containing @keyframes or .class-name definitions.
"""


def generate_tailwind_styles(website_plan: Dict) -> List[GeneratedCode]:
    """
    Generate Tailwind CSS configuration and styles.
    
    LLM decides: custom utilities, animations
    Hardcoded: base structure, theme tokens
    """
    logger.info("="*60)
    logger.info("TAILWIND/CSS GENERATION")
    logger.info("="*60)
    
    colors = website_plan.get("color_scheme", {})
    font_family = website_plan.get("font_family", "Inter")
    style = website_plan.get("style", "modern")
    use_animations = website_plan.get("use_animations", True)
    
    logger.info("--- Colors from website_plan ---")
    logger.info(f"  primary: {colors.get('primary', '#6366f1')}")
    logger.info(f"  secondary: {colors.get('secondary', '#818cf8')}")
    logger.info(f"  background: {colors.get('background', '#0f172a')}")
    logger.info(f"  text: {colors.get('text', '#f8fafc')}")
    logger.info(f"  style: {style}")
    
    generated_files = []
    
    # Get custom utilities (LLM or fallback)
    custom_utilities = _get_custom_utilities_llm(colors, style, use_animations)
    
    # Generate index.css [HARDCODED structure + LLM utilities]
    css_code = _generate_index_css(colors, font_family, custom_utilities)
    generated_files.append(GeneratedCode(
        filename="index.css",
        filepath="src/index.css",
        content=css_code,
        component_type="style"
    ))
    logger.info("  ✓ index.css [HARDCODED structure + LLM utilities]")
    
    # Generate tailwind.config.js [HARDCODED structure + colors from plan]
    tailwind_config = _generate_tailwind_config(colors, font_family, style, use_animations)
    generated_files.append(GeneratedCode(
        filename="tailwind.config.js",
        filepath="tailwind.config.js",
        content=tailwind_config,
        component_type="config"
    ))
    logger.info("  ✓ tailwind.config.js [HARDCODED structure + plan colors]")
    
    # Generate postcss.config.js [100% HARDCODED]
    postcss_config = _generate_postcss_config()
    generated_files.append(GeneratedCode(
        filename="postcss.config.js",
        filepath="postcss.config.js",
        content=postcss_config,
        component_type="config"
    ))
    logger.info("  ✓ postcss.config.js [100% HARDCODED]")
    
    return generated_files


def _get_custom_utilities_llm(colors: Dict, style: str, use_animations: bool) -> str:
    """
    Get custom CSS utilities using LLM.
    Falls back to hardcoded utilities if LLM fails.
    """
    logger.info("--- Custom utilities generation ---")
    
    try:
        llm = get_fast_llm(temperature=0.5)
        
        prompt = CUSTOM_UTILITIES_PROMPT.format(
            style=style,
            primary=colors.get("primary", "#6366f1"),
            secondary=colors.get("secondary", "#818cf8"),
            accent=colors.get("accent", "#22d3ee"),
            background=colors.get("background", "#0f172a"),
            text=colors.get("text", "#f8fafc"),
            use_animations="yes" if use_animations else "no"
        )
        
        logger.info("  [LLM] Calling LLM for custom utilities...")
        response = llm.invoke(prompt)
        
        utilities = _extract_css(response.content)
        
        if utilities and len(utilities) > 50:
            logger.info(f"  [LLM] SUCCESS - Generated {len(utilities)} chars of CSS")
            return utilities
        else:
            logger.warning("  [LLM] Response too short, using FALLBACK")
            return _get_fallback_utilities(colors, style, use_animations)
            
    except Exception as e:
        logger.error(f"  [LLM] Error: {e}")
        logger.info("  [FALLBACK] Using hardcoded utilities")
        return _get_fallback_utilities(colors, style, use_animations)


def _extract_css(response: str) -> str:
    """Extract CSS from LLM response."""
    # Remove markdown code blocks if present
    import re
    patterns = [
        r'```css\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # If no code blocks, check if it starts with /* or @
    if response.strip().startswith(('/*', '@keyframes', '.')):
        return response.strip()
    
    return ""


def _get_fallback_utilities(colors: Dict, style: str, use_animations: bool) -> str:
    """Fallback hardcoded utilities when LLM fails."""
    primary = colors.get("primary", "#6366f1")
    
    utilities = []
    
    # Base animation utilities [HARDCODED]
    if use_animations:
        utilities.append("""
/* Animation utilities [HARDCODED FALLBACK] */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
  50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8); }
}

.animate-pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
""")
    
    # Style-specific utilities [HARDCODED]
    if style == "creative":
        utilities.append(f"""
/* Creative style utilities [HARDCODED FALLBACK] */
.gradient-text {{
  background: linear-gradient(135deg, {primary}, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

.creative-border {{
  border: 2px solid transparent;
  background: linear-gradient(var(--color-background), var(--color-background)) padding-box,
              linear-gradient(135deg, {primary}, #ec4899) border-box;
  border-radius: 12px;
}}
""")
    elif style == "modern":
        utilities.append(f"""
/* Modern style utilities [HARDCODED FALLBACK] */
.glass-effect {{
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}}

.modern-shadow {{
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}}

.hover-lift {{
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.hover-lift:hover {{
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}}
""")
    elif style == "minimal":
        utilities.append("""
/* Minimal style utilities [HARDCODED FALLBACK] */
.subtle-shadow {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.clean-border {
  border: 1px solid rgba(0, 0, 0, 0.1);
}
""")
    elif style == "bold":
        utilities.append(f"""
/* Bold style utilities [HARDCODED FALLBACK] */
.bold-gradient {{
  background: linear-gradient(135deg, {primary}, #f97316);
}}

.bold-shadow {{
  box-shadow: 0 4px 0 {primary};
}}

.bold-text {{
  text-shadow: 2px 2px 0 {primary};
}}
""")
    
    return "\n".join(utilities)


def _generate_index_css(colors: Dict, font_family: str, custom_utilities: str) -> str:
    """Generate index.css with structure [HARDCODED] + utilities [LLM/FALLBACK]."""
    font_import_url = FONT_IMPORTS.get(font_family, FONT_IMPORTS["Inter"])
    font_import = f"@import url('{font_import_url}');"
    
    return BASE_CSS_STRUCTURE.format(
        font_import=font_import,
        primary=colors.get("primary", "#6366f1"),
        secondary=colors.get("secondary", "#818cf8"),
        accent=colors.get("accent", "#22d3ee"),
        background=colors.get("background", "#0f172a"),
        text=colors.get("text", "#f8fafc"),
        font_family=font_family,
        custom_utilities=custom_utilities
    )


def _generate_tailwind_config(colors: Dict, font_family: str, style: str, use_animations: bool) -> str:
    """Generate tailwind.config.js [HARDCODED structure + dynamic colors]."""
    # Add animation config if needed
    animation_config = ""
    if use_animations:
        animation_config = """animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'float': 'float 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 5px rgba(99, 102, 241, 0.5)' },
          '50%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.8)' },
        },
      },"""
    
    return TAILWIND_CONFIG_STRUCTURE % (
        colors.get("primary", "#6366f1"),
        colors.get("secondary", "#818cf8"),
        colors.get("accent", "#22d3ee"),
        colors.get("background", "#0f172a"),
        colors.get("text", "#f8fafc"),
        font_family,
        animation_config
    )


def _generate_postcss_config() -> str:
    """Generate postcss.config.js [100% HARDCODED]."""
    return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
