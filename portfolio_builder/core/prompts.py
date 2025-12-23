"""
Prompt Templates for Portfolio Builder Agents.

Centralized prompts for all agent nodes in the LangGraph workflow.
"""

# ============================================================
# RESUME PARSER PROMPTS
# ============================================================

RESUME_PARSER_PROMPT = """You are an expert resume parser. Your task is to extract structured information from the provided resume text.

<RESUME_TEXT>
{resume_text}
</RESUME_TEXT>

Extract the following information and return it as a valid JSON object. If a field is not present in the resume, use null or an empty array as appropriate.

Required JSON structure:
{{
    "name": "Full name of the person",
    "email": "Email address or null",
    "phone": "Phone number or null",
    "linkedin": "LinkedIn URL or null",
    "github": "GitHub URL or null",
    "website": "Personal website URL or null",
    "summary": "Professional summary or objective statement or null",
    "skills": ["skill1", "skill2", ...],
    "projects": [
        {{
            "title": "Project name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "link": "Project URL or null",
            "github_link": "GitHub repo URL or null"
        }}
    ],
    "experience": [
        {{
            "company": "Company name",
            "role": "Job title",
            "duration": "Start - End dates",
            "description": "Role description",
            "highlights": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "education": [
        {{
            "institution": "University/School name",
            "degree": "Degree type",
            "field": "Field of study",
            "year": "Graduation year",
            "gpa": "GPA or null"
        }}
    ],
    "certifications": [
        {{
            "name": "Certification name",
            "issuer": "Issuing organization",
            "date": "Date obtained",
            "link": "Verification URL or null"
        }}
    ],
    "languages": ["Language 1", "Language 2"],
    "interests": ["Interest 1", "Interest 2"]
}}

IMPORTANT:
1. Extract ONLY information explicitly present in the resume
2. For skills, list all technical and soft skills mentioned
3. For projects, include personal, academic, and professional projects
4. Normalize URLs to include https:// if missing
5. Return ONLY the JSON object, no additional text

JSON Output:"""


# ============================================================
# WEBSITE PLANNER PROMPTS
# ============================================================

WEBSITE_PLANNER_PROMPT = """You are an expert web designer and portfolio strategist. Based on the user's requirements and their resume data, create a comprehensive website plan.

<USER_REQUIREMENTS>
{user_prompt}
</USER_REQUIREMENTS>

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

Analyze the resume and user requirements to create a website plan. Consider:
1. The user's profession and industry
2. The amount and type of content available
3. User's stated preferences (if any)
4. Modern web design best practices

Return a JSON object with the following structure:
{{
    "style": "minimal" | "modern" | "creative" | "professional" | "bold",
    "color_scheme": {{
        "primary": "#hexcode",
        "secondary": "#hexcode",
        "accent": "#hexcode",
        "background": "#hexcode",
        "text": "#hexcode"
    }},
    "sections": ["hero", "about", "skills", "projects", "experience", "contact"],
    "layout": "single_page" | "multi_section",
    "use_animations": true | false,
    "animation_library": "framer-motion" | null,
    "tech_stack": ["react", "tailwind", "framer-motion"],
    "font_family": "Inter" | "Roboto" | "Poppins" | "Outfit" | "Space Grotesk",
    "dark_mode": true | false,
    "navigation_style": "fixed" | "sticky" | "static",
    "design_rationale": "Brief explanation of design choices"
}}

DECISION RULES:
1. Style Selection:
   - "minimal": Clean, whitespace-heavy, for serious professionals
   - "modern": Sleek gradients, cards, for tech professionals
   - "creative": Bold colors, unique layouts, for designers/artists
   - "professional": Traditional, formal, for corporate roles
   - "bold": High contrast, standout elements, for innovators

2. Sections to Include:
   - ALWAYS include: hero, about, contact
   - Include "projects" ONLY if resume has projects
   - Include "skills" ONLY if resume has skills
   - Include "experience" ONLY if resume has work experience

3. Animations:
   - Enable for creative/modern styles
   - Disable if user requests "simple" or "fast loading"

4. Color Scheme:
   - Match to industry (tech: blues/purples, creative: vibrant, corporate: conservative)
   - Ensure good contrast for accessibility

Return ONLY the JSON object, no additional text.

JSON Output:"""


# ============================================================
# SECTION GENERATOR PROMPTS
# ============================================================

HERO_SECTION_PROMPT = """You are a creative copywriter specializing in portfolio websites. Generate compelling hero section content.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Create hero section content that immediately captures attention and communicates the person's value proposition.

Return a JSON object:
{{
    "headline": "Catchy main headline (e.g., 'Full Stack Developer')",
    "tagline": "Engaging subtitle (1-2 sentences about what they do)",
    "cta_primary": {{
        "text": "Primary button text (e.g., 'View My Work')",
        "target_section": "projects" | "contact"
    }},
    "cta_secondary": {{
        "text": "Secondary button text (e.g., 'Download Resume')",
        "action": "download_resume" | "external_link"
    }},
    "greeting": "Optional greeting (e.g., 'Hi, I'm' or 'Hello, I'm')",
    "background_style": "gradient" | "pattern" | "solid" | "animated",
    "show_social_links": true | false,
    "typing_animation_texts": ["Developer", "Designer", "Creator"] // if animations enabled
}}

Make it {style} style. Be creative but professional.

JSON Output:"""


ABOUT_SECTION_PROMPT = """Generate compelling "About Me" section content for a portfolio website.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Create an engaging about section that tells the person's story.

Return a JSON object:
{{
    "title": "Section title (e.g., 'About Me', 'Who I Am')",
    "bio_paragraphs": [
        "First paragraph - introduction and current role",
        "Second paragraph - background and journey",
        "Third paragraph - what drives them (optional)"
    ],
    "key_facts": [
        {{"icon": "briefcase", "label": "Experience", "value": "X+ Years"}},
        {{"icon": "code", "label": "Projects", "value": "X+ Projects"}},
        {{"icon": "graduation-cap", "label": "Education", "value": "Degree Name"}}
    ],
    "profile_image_placeholder": true,
    "layout": "text-left" | "text-right" | "centered"
}}

Tone should match {style} style. Be authentic and engaging.

JSON Output:"""


SKILLS_SECTION_PROMPT = """Generate a visually appealing skills section for a portfolio website.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Organize and present skills in an impactful way.

Return a JSON object:
{{
    "title": "Section title (e.g., 'Skills & Technologies', 'Tech Stack')",
    "subtitle": "Brief intro to skills section",
    "categories": [
        {{
            "name": "Frontend",
            "skills": [
                {{"name": "React", "proficiency": 90, "icon": "react"}},
                {{"name": "TypeScript", "proficiency": 85, "icon": "typescript"}}
            ]
        }},
        {{
            "name": "Backend",
            "skills": [...]
        }}
    ],
    "display_style": "cards" | "bars" | "tags" | "icons",
    "show_proficiency": true | false,
    "featured_skills": ["skill1", "skill2", "skill3"]
}}

Group related skills logically. Match {style} style.

JSON Output:"""


PROJECTS_SECTION_PROMPT = """Generate an impressive projects showcase section for a portfolio website.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Create compelling project cards that showcase achievements.

Return a JSON object:
{{
    "title": "Section title (e.g., 'Featured Projects', 'My Work')",
    "subtitle": "Brief intro to projects",
    "projects": [
        {{
            "title": "Project Name",
            "description": "Engaging 2-3 sentence description",
            "technologies": ["React", "Node.js", "MongoDB"],
            "image_placeholder": "project-1",
            "links": {{
                "live": "URL or null",
                "github": "URL or null"
            }},
            "featured": true | false,
            "category": "Web App" | "Mobile" | "AI/ML" | "Other"
        }}
    ],
    "layout": "grid" | "carousel" | "masonry",
    "show_filters": true | false,
    "filter_categories": ["All", "Web", "Mobile", "AI"]
}}

Highlight best projects first. Make descriptions action-oriented.

JSON Output:"""


EXPERIENCE_SECTION_PROMPT = """Generate a professional experience/timeline section for a portfolio website.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Present work experience in an engaging timeline format.

Return a JSON object:
{{
    "title": "Section title (e.g., 'Experience', 'Career Journey')",
    "subtitle": "Brief intro",
    "experiences": [
        {{
            "company": "Company Name",
            "role": "Job Title",
            "duration": "Jan 2022 - Present",
            "location": "City, Country or Remote",
            "description": "Brief role overview",
            "highlights": [
                "Achievement with impact metrics",
                "Key responsibility or contribution"
            ],
            "technologies": ["Tech1", "Tech2"],
            "logo_placeholder": "company-1"
        }}
    ],
    "layout": "timeline" | "cards" | "list",
    "show_company_logos": true | false
}}

Use action verbs and quantify achievements where possible.

JSON Output:"""


CONTACT_SECTION_PROMPT = """Generate a contact section for a portfolio website.

<RESUME_DATA>
{resume_data}
</RESUME_DATA>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Create an inviting contact section that encourages outreach.

Return a JSON object:
{{
    "title": "Section title (e.g., 'Get In Touch', 'Let's Connect')",
    "subtitle": "Encouraging message to reach out",
    "cta_message": "Brief call-to-action text",
    "show_form": true | false,
    "form_fields": ["name", "email", "message"],
    "contact_info": {{
        "email": "email@example.com",
        "phone": "phone or null",
        "location": "City, Country or null"
    }},
    "social_links": [
        {{"platform": "github", "url": "..."}},
        {{"platform": "linkedin", "url": "..."}},
        {{"platform": "twitter", "url": "..."}}
    ],
    "availability_status": "Available for opportunities" | "Open to projects" | null
}}

Make it warm and approachable. Match {style} style.

JSON Output:"""


# ============================================================
# CODE GENERATOR PROMPTS
# ============================================================

CODE_GENERATOR_SYSTEM_PROMPT = """You are an expert React and Tailwind CSS developer. You generate clean, production-ready code for portfolio websites.

KEY REQUIREMENTS:
1. Use React functional components with hooks
2. Use Tailwind CSS for ALL styling (no inline styles or CSS files except index.css)
3. Components must be responsive (mobile-first)
4. Use modern JavaScript (ES6+)
5. Include proper imports and exports
6. Add helpful comments for complex logic
7. Ensure accessibility (aria labels, semantic HTML)
8. Use Lucide React for icons (import from 'lucide-react')

CODE STYLE:
- 2 space indentation
- Single quotes for strings
- Trailing commas
- Descriptive variable names
- Component names in PascalCase
- File names match component names
"""


CODE_GENERATOR_COMPONENT_PROMPT = """Generate a React component for the {section_name} section.

<SECTION_CONTENT>
{section_content}
</SECTION_CONTENT>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Generate a complete, production-ready React component. 

Requirements:
1. Use the exact content from SECTION_CONTENT
2. Apply {style} design style with colors: {colors}
3. Use font: {font_family}
4. {"Include Framer Motion animations" if use_animations else "No animations needed"}
5. Make it fully responsive

Return ONLY the complete component code, no explanations. Start with imports.

```jsx
// Your component code here
```"""


CODE_GENERATOR_APP_PROMPT = """Generate the main App.jsx file that composes all section components.

<SECTIONS>
{sections}
</SECTIONS>

<WEBSITE_PLAN>
{website_plan}
</WEBSITE_PLAN>

Generate App.jsx that:
1. Imports all section components
2. Includes a responsive navigation bar
3. Assembles sections in correct order
4. Handles smooth scrolling to sections
5. Applies global styles from the plan

Return ONLY the complete App.jsx code.

```jsx
// Your App.jsx code here
```"""


# ============================================================
# VALIDATOR PROMPTS
# ============================================================

VALIDATOR_PROMPT = """You are a code quality expert. Analyze this React/JSX code for errors and issues.

<CODE>
{code}
</CODE>

<FILENAME>
{filename}
</FILENAME>

Check for:
1. JSX syntax errors
2. Missing or incorrect imports
3. Invalid Tailwind CSS classes
4. Undefined variables or components
5. Accessibility issues
6. React best practices violations

Return a JSON object:
{{
    "is_valid": true | false,
    "errors": [
        {{
            "line": 10,
            "message": "Description of error",
            "severity": "error" | "warning",
            "rule": "jsx-syntax" | "missing-import" | "invalid-tailwind" | "undefined-var" | "accessibility" | "best-practice",
            "suggestion": "How to fix it"
        }}
    ]
}}

Return ONLY the JSON object.

JSON Output:"""


FIXER_PROMPT = """You are a code repair expert. Fix the identified errors in this React component.

<CODE>
{code}
</CODE>

<ERRORS>
{errors}
</ERRORS>

Fix ALL the identified errors while:
1. Preserving the original functionality
2. Maintaining code style consistency
3. Not introducing new issues

Return ONLY the fixed complete code, no explanations.

```jsx
// Fixed component code here
```"""


# ============================================================
# ASSEMBLER PROMPTS
# ============================================================

README_TEMPLATE = """# {name}'s Portfolio Website

A modern, responsive portfolio website built with React and Tailwind CSS.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 📁 Project Structure

```
├── src/
│   ├── components/     # React components
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
└── package.json        # Dependencies
```

## 🛠️ Built With

{tech_stack}

## 📝 Customization

- Update content in component files under `src/components/`
- Modify colors in `tailwind.config.js`
- Add images to `public/` folder

## 📄 License

MIT License - feel free to use this for your own portfolio!

---
Generated with ❤️ by Auto Portfolio Builder
"""
