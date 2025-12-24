"""
React Component Generator - LLM-based code generation.

Uses LLM with strict prompts to generate React/JSX components.
"""

import re
from typing import Dict, Any, List, Optional

from portfolio_builder.core.state import PortfolioBuilderState, GeneratedCode
from portfolio_builder.core.llm_config import get_code_llm
from portfolio_builder.core.logger import get_logger
from portfolio_builder.utils.helpers import format_component_name

logger = get_logger("react_generator")


# Strict prompts for each section type
COMPONENT_PROMPTS = {
    "hero": """Generate a React Hero section component with the following requirements:

PERSON DATA:
- Name: {name}
- Headline: {headline}
- Tagline: {tagline}
- GitHub: {github}
- LinkedIn: {linkedin}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}
- Font: {font_family}
- Style: {style}

Generate a modern, responsive Hero component using:
- React functional component
- Tailwind CSS classes
- lucide-react icons (Github, Linkedin, Mail, ArrowDown)
- The EXACT colors specified above using inline styles or Tailwind

Return ONLY the JSX code, no explanations. Start with 'import React' and end with 'export default Hero;'
""",

    "about": """Generate a React About section component with the following requirements:

PERSON DATA:
- Name: {name}
- Bio: {bio}
- Key Facts: {facts}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}

Generate a clean About section with:
- Centered heading with accent underline
- Bio paragraph(s)
- Optional key facts/stats grid
- lucide-react User icon for avatar placeholder

Return ONLY the JSX code. Start with 'import React' and end with 'export default About;'
""",

    "skills": """Generate a React Skills section component:

SKILLS DATA:
{skills_data}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}

Generate a Skills section with:
- Grid/card layout for skill categories
- Skill tags/badges
- Responsive design

Return ONLY the JSX code. Start with 'import React' and end with 'export default Skills;'
""",

    "projects": """Generate a React Projects section component:

PROJECTS DATA:
{projects_data}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}

Generate a Projects showcase with:
- Card grid layout (2-3 columns)
- Project title, description, tech stack
- Links to live demo and GitHub
- Hover effects

Return ONLY the JSX code. Start with 'import React' and end with 'export default Projects;'
""",

    "experience": """Generate a React Experience/Timeline section component:

EXPERIENCE DATA:
{experience_data}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}

Generate a timeline-style Experience section with:
- Vertical timeline with dots
- Cards for each position
- Company, role, duration, highlights

Return ONLY the JSX code. Start with 'import React' and end with 'export default Experience;'
""",

    "contact": """Generate a React Contact section component:

CONTACT DATA:
- Email: {email}
- GitHub: {github}
- LinkedIn: {linkedin}

STYLE REQUIREMENTS:
- Background color: {background_color}
- Text color: {text_color}
- Primary accent color: {primary_color}

Generate a Contact section with:
- Centered layout
- CTA buttons for email/LinkedIn
- Social icons
- Copyright footer

Return ONLY the JSX code. Use lucide-react icons. Start with 'import React' and end with 'export default Contact;'
"""
}


def generate_react_components(
    sections_content: List[Dict],
    website_plan: Dict,
    resume_data: Dict
) -> List[GeneratedCode]:
    """
    Generate React components using LLM for each section.
    
    Args:
        sections_content: List of section content dicts
        website_plan: Website plan with colors, style, etc.
        resume_data: Parsed resume data
        
    Returns:
        List of GeneratedCode objects
    """
    logger.info("="*60)
    logger.info("REACT COMPONENT GENERATION (LLM-based)")
    logger.info("="*60)
    
    colors = website_plan.get("color_scheme", {})
    logger.info("--- Using colors from website_plan ---")
    logger.info(f"  background: {colors.get('background', '#0f172a')}")
    logger.info(f"  text: {colors.get('text', '#f8fafc')}")
    logger.info(f"  primary: {colors.get('primary', '#6366f1')}")
    
    # Get LLM
    try:
        llm = get_code_llm(temperature=0.3)
        llm_available = True
        logger.info("  [LLM] LLM initialized successfully")
    except Exception as e:
        logger.warning(f"  [LLM] Not available: {e}")
        llm = None
        llm_available = False
    
    generated_files = []
    
    for section in sections_content:
        section_name = section.get("section_name", "")
        section_content = section.get("content", {})
        
        if not section_name:
            continue
        
        logger.info(f"\n--- Generating {section_name.upper()} component ---")
        
        if llm_available:
            component_code = _generate_with_llm(
                llm, section_name, section_content, website_plan, resume_data
            )
        else:
            component_code = _generate_fallback(
                section_name, section_content, website_plan, resume_data
            )
        
        if component_code:
            component_name = format_component_name(section_name)
            generated_files.append(GeneratedCode(
                filename=f"{component_name}.jsx",
                filepath=f"src/components/{component_name}.jsx",
                content=component_code,
                component_type="component"
            ))
            logger.info(f"  ✓ {component_name}.jsx generated")
    
    logger.info(f"\n--- Generated {len(generated_files)} React components ---")
    return generated_files


def _generate_with_llm(
    llm,
    section_name: str,
    section_content: Dict,
    website_plan: Dict,
    resume_data: Dict
) -> Optional[str]:
    """Generate component using LLM with strict prompt."""
    colors = website_plan.get("color_scheme", {})
    
    # Build prompt context
    context = {
        "name": resume_data.get("name", "Developer"),
        "headline": section_content.get("headline", "Full Stack Developer"),
        "tagline": section_content.get("tagline", "Building amazing experiences"),
        "github": resume_data.get("github", ""),
        "linkedin": resume_data.get("linkedin", ""),
        "email": resume_data.get("email", ""),
        "bio": section_content.get("bio_paragraphs", [""])[0] if section_content.get("bio_paragraphs") else "",
        "facts": str(section_content.get("key_facts", [])),
        "skills_data": str(section_content.get("categories", resume_data.get("skills", []))),
        "projects_data": str(section_content.get("projects", resume_data.get("projects", []))),
        "experience_data": str(section_content.get("experiences", resume_data.get("experience", []))),
        "background_color": colors.get("background", "#0f172a"),
        "text_color": colors.get("text", "#f8fafc"),
        "primary_color": colors.get("primary", "#6366f1"),
        "font_family": website_plan.get("font_family", "Inter"),
        "style": website_plan.get("style", "modern"),
    }
    
    # Get prompt template
    prompt_template = COMPONENT_PROMPTS.get(section_name.lower())
    
    if not prompt_template:
        logger.warning(f"  [LLM] No prompt template for {section_name}, using fallback")
        return _generate_fallback(section_name, section_content, website_plan, resume_data)
    
    try:
        prompt = prompt_template.format(**context)
        logger.info(f"  [LLM] Calling LLM for {section_name}...")
        
        response = llm.invoke(prompt)
        code = _extract_jsx_code(response.content)
        
        if code:
            logger.info(f"  [LLM] SUCCESS - Generated {len(code)} chars")
            return _sanitize_jsx(code)
        else:
            logger.warning(f"  [LLM] Empty response, using fallback")
            return _generate_fallback(section_name, section_content, website_plan, resume_data)
            
    except Exception as e:
        logger.error(f"  [LLM] Error: {e}")
        return _generate_fallback(section_name, section_content, website_plan, resume_data)


def _extract_jsx_code(response: str) -> Optional[str]:
    """Extract JSX code block from LLM response."""
    # Try to extract from code blocks
    patterns = [
        r'```jsx\s*(.*?)\s*```',
        r'```javascript\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # If no code blocks, check if response starts with import
    if response.strip().startswith('import'):
        return response.strip()
    
    return None


def _sanitize_jsx(code: str) -> str:
    """Sanitize JSX code to ensure it's valid."""
    # Remove any markdown artifacts
    code = re.sub(r'^```\w*\n?', '', code)
    code = re.sub(r'\n?```$', '', code)
    
    # Ensure proper line endings
    code = code.replace('\r\n', '\n')
    
    # Add newline at end if missing
    if not code.endswith('\n'):
        code += '\n'
    
    return code


def _generate_fallback(
    section_name: str,
    section_content: Dict,
    website_plan: Dict,
    resume_data: Dict
) -> str:
    """Generate fallback component when LLM fails."""
    logger.info(f"  [FALLBACK] Using template for {section_name}")
    
    colors = website_plan.get("color_scheme", {})
    bg = colors.get("background", "#0f172a")
    text = colors.get("text", "#f8fafc")
    primary = colors.get("primary", "#6366f1")
    
    component_name = format_component_name(section_name)
    
    return f'''import React from 'react';

const {component_name} = () => {{
  return (
    <section 
      id="{section_name.lower()}" 
      className="py-20 px-4 min-h-screen flex items-center justify-center"
      style={{{{ backgroundColor: '{bg}', color: '{text}' }}}}
    >
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-4xl font-bold mb-4">{section_name.title()}</h2>
        <div className="w-24 h-1 mx-auto mb-8" style={{{{ backgroundColor: '{primary}' }}}}></div>
        <p className="text-xl opacity-80">Content for {section_name} section</p>
      </div>
    </section>
  );
}};

export default {component_name};
'''


def generate_app_component(
    sections_content: List[Dict],
    website_plan: Dict,
    resume_data: Dict
) -> GeneratedCode:
    """Generate the main App.jsx component."""
    logger.info("--- Generating App.jsx ---")
    
    colors = website_plan.get("color_scheme", {})
    bg = colors.get("background", "#0f172a")
    text = colors.get("text", "#f8fafc")
    primary = colors.get("primary", "#6366f1")
    
    # Sort sections by order
    sections = sorted(sections_content, key=lambda x: x.get("order", 0))
    
    # Generate imports and components
    imports = []
    components = []
    nav_items = []
    
    for section in sections:
        name = section.get("section_name", "")
        if name:
            component_name = format_component_name(name)
            imports.append(f"import {component_name} from './components/{component_name}';")
            components.append(f"      <{component_name} />")
            nav_items.append(f'{{ id: "{name.lower()}", label: "{name.title()}" }}')
    
    imports_str = "\n".join(imports)
    components_str = "\n".join(components)
    nav_items_str = ", ".join(nav_items)
    
    app_code = f'''import React from 'react';
import {{ Menu, X }} from 'lucide-react';
{imports_str}

const navItems = [{nav_items_str}];

function App() {{
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  
  const scrollToSection = (id) => {{
    document.getElementById(id)?.scrollIntoView({{ behavior: 'smooth' }});
    setMobileMenuOpen(false);
  }};

  return (
    <div className="min-h-screen" style={{{{ backgroundColor: '{bg}', color: '{text}' }}}}>
      {{/* Navigation */}}
      <nav 
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-sm border-b"
        style={{{{ backgroundColor: '{bg}dd', borderColor: '{primary}33' }}}}
      >
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="#hero" className="text-xl font-bold" style={{{{ color: '{primary}' }}}}>Portfolio</a>
          
          {{/* Desktop Nav */}}
          <ul className="hidden md:flex items-center gap-8">
            {{navItems.map((item) => (
              <li key={{item.id}}>
                <button 
                  onClick={{() => scrollToSection(item.id)}}
                  className="opacity-80 hover:opacity-100 transition-opacity"
                >
                  {{item.label}}
                </button>
              </li>
            ))}}
          </ul>
          
          {{/* Mobile Menu Button */}}
          <button 
            className="md:hidden"
            onClick={{() => setMobileMenuOpen(!mobileMenuOpen)}}
          >
            {{mobileMenuOpen ? <X size={{24}} /> : <Menu size={{24}} />}}
          </button>
        </div>
        
        {{/* Mobile Nav */}}
        {{mobileMenuOpen && (
          <div className="md:hidden border-t" style={{{{ borderColor: '{primary}33' }}}}>
            <ul className="px-4 py-4 space-y-4">
              {{navItems.map((item) => (
                <li key={{item.id}}>
                  <button 
                    onClick={{() => scrollToSection(item.id)}}
                    className="opacity-80 hover:opacity-100 transition-opacity block w-full text-left"
                  >
                    {{item.label}}
                  </button>
                </li>
              ))}}
            </ul>
          </div>
        )}}
      </nav>

      {{/* Sections */}}
      <main className="pt-16">
{components_str}
      </main>
    </div>
  );
}}

export default App;
'''
    
    logger.info("  ✓ App.jsx generated with dynamic colors")
    
    return GeneratedCode(
        filename="App.jsx",
        filepath="src/App.jsx",
        content=app_code,
        component_type="page"
    )


def generate_main_entry() -> GeneratedCode:
    """Generate main.jsx entry point."""
    code = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
    return GeneratedCode(
        filename="main.jsx",
        filepath="src/main.jsx",
        content=code,
        component_type="page"
    )
