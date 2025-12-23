# Auto Portfolio Builder - Workflow & File Connections

## High-Level Flow

```
User Input (resume + prompt)
        │
        ▼
┌───────────────────┐
│     app.py        │  ◄── Entry Point
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│    core/graph.py  │  ◄── LangGraph Workflow Definition
└─────────┬─────────┘
          │
          ▼
    [ Workflow Execution ]
          │
          ▼
    Generated Portfolio
```

---

## File-by-File Connection Map

### 1. Entry Point: `app.py`

```python
# app.py imports:
from core.state import create_initial_state    # Creates the initial workflow state
from core.graph import get_workflow            # Gets the compiled LangGraph workflow
from services.resume_parser import ...         # Parses resume files
from utils.helpers import generate_project_id  # Generates unique IDs
```

**What it does:**
- Accepts user prompt + resume (file or text)
- Creates initial `PortfolioBuilderState`
- Calls `workflow.invoke(initial_state)`
- Returns the result (output_path, zip_path, etc.)

---

### 2. State Schema: `core/state.py`

```python
# Defines the shared state that flows through ALL nodes:
class PortfolioBuilderState(TypedDict):
    user_prompt: str              # User's requirements
    resume_text: str              # Raw resume
    resume_parsed: ResumeData     # Structured resume data
    website_plan: WebsitePlan     # Design decisions
    sections_content: List[...]   # Generated section content
    generated_files: List[...]    # React code files
    validation_result: ...        # Validation status
    output_path: str              # Final output location
```

**Connection:** Every node reads from and writes to this state.

---

### 3. Graph Definition: `core/graph.py`

```python
# graph.py imports ALL nodes:
from agents.planner import resume_parser_node, website_planner_node
from agents.executors import hero_section_agent, about_section_agent, ...
from agents.codegen import frontend_generator_node
from agents.validator import validator_node
from agents.assembler import final_assembler_node
from core.routing import check_resume_parsed, should_revalidate
```

**What it does:**
- Creates `StateGraph(PortfolioBuilderState)`
- Adds all nodes to the graph
- Defines edges (connections between nodes)
- Compiles the workflow

**Graph Structure:**
```
resume_parser ──► website_planner ──► section_agents ──► aggregate
                                                              │
                                                              ▼
                     ◄────── validator ◄────── code_generator ◄┘
                     │           │
                     │      (retry loop)
                     ▼
                 assembler ──► END
```

---

### 4. Routing Logic: `core/routing.py`

```python
# Used as conditional edges in graph.py:

def check_resume_parsed(state) -> "continue" | "error"
    # Checks if resume was parsed successfully

def should_revalidate(state) -> "regenerate" | "assemble" | "assemble_with_warnings"
    # Decides whether to retry code generation or proceed
```

**Connection:** Called by `graph.py` for conditional branching.

---

### 5. LLM Config: `core/llm_config.py`

```python
# Provides LLM instances to all agents:
get_reasoning_llm()  # llama-3.1-70b - for complex tasks (planner)
get_fast_llm()       # llama-3.1-8b - for simple tasks (section content)
get_code_llm()       # llama-3.1-70b - for code generation
```

**Connection:** Imported by every agent node that needs LLM.

---

### 6. Prompts: `core/prompts.py`

Contains all prompt templates:
- `RESUME_PARSER_PROMPT`
- `WEBSITE_PLANNER_PROMPT`
- `HERO_SECTION_PROMPT`, `ABOUT_SECTION_PROMPT`, etc.
- `CODE_GENERATOR_COMPONENT_PROMPT`
- `VALIDATOR_PROMPT`, `FIXER_PROMPT`

**Connection:** Imported by each respective agent node.

---

## Node Execution Flow

### Node 1: `resume_parser_node` (`agents/planner/resume_parser_node.py`)

```
Input:  state.resume_text
Output: state.resume_parsed, state.parsing_confidence
```

```python
# Imports:
from core.llm_config import get_reasoning_llm
from core.prompts import RESUME_PARSER_PROMPT
from utils.text_cleaner import clean_resume_text, extract_urls
```

---

### Node 2: `website_planner_node` (`agents/planner/website_planner_node.py`)

```
Input:  state.resume_parsed, state.user_prompt
Output: state.website_plan, state.sections_to_generate
```

```python
# Imports:
from core.llm_config import get_reasoning_llm
from core.prompts import WEBSITE_PLANNER_PROMPT
```

---

### Nodes 3-8: Section Agents (`agents/executors/*.py`)

Each section agent follows the same pattern:

```
Input:  state.resume_parsed, state.website_plan
Output: state.sections_content (appended)
```

```python
# Example: hero_section_agent.py imports:
from core.llm_config import get_fast_llm
from core.prompts import HERO_SECTION_PROMPT
from core.state import SectionContent
```

---

### Node 9: `frontend_generator_node` (`agents/codegen/frontend_generator.py`)

```
Input:  state.sections_content, state.website_plan
Output: state.generated_files (React components + configs)
```

```python
# Imports:
from core.llm_config import get_code_llm
from core.prompts import CODE_GENERATOR_SYSTEM_PROMPT, CODE_GENERATOR_COMPONENT_PROMPT
from core.state import GeneratedCode
```

---

### Node 10: `validator_node` (`agents/validator/validator_agent.py`)

```
Input:  state.generated_files
Output: state.validation_result, (potentially fixed) state.generated_files
```

```python
# Imports:
from core.llm_config import get_code_llm
from core.prompts import VALIDATOR_PROMPT, FIXER_PROMPT
from core.state import ValidationResult, ValidationError
```

**Special:** If validation fails and attempts < max, returns to `frontend_generator_node`.

---

### Node 11: `final_assembler_node` (`agents/assembler/final_assembler.py`)

```
Input:  state.generated_files, state.project_id
Output: state.output_path, state.zip_path, state.preview_url
```

```python
# Imports:
from services.file_service import get_file_service
from services.preview_service import get_preview_service
from utils.file_utils import create_zip
```

---

## Services Layer

### `services/resume_parser.py`
- Called by `app.py` to extract text from PDF/DOCX
- Uses `pypdf` for PDF parsing

### `services/file_service.py`
- Called by `final_assembler_node`
- Writes generated files to disk
- Creates ZIP archives

### `services/preview_service.py`
- Called by `final_assembler_node`
- Generates standalone HTML preview

---

## Utilities

### `utils/text_cleaner.py`
- Called by `resume_parser_node`
- Functions: `clean_resume_text()`, `extract_urls()`, `normalize_skills()`

### `utils/file_utils.py`
- Called by services and assembler
- Functions: `create_project_structure()`, `write_file()`, `create_zip()`

### `utils/helpers.py`
- Called throughout
- Functions: `safe_json_parse()`, `format_component_name()`, `extract_code_from_response()`

---

## Data Flow Summary

```
┌─────────────┐    resume_text    ┌─────────────────┐    resume_parsed    ┌─────────────────┐
│   app.py    │ ───────────────► │  resume_parser  │ ────────────────► │ website_planner │
└─────────────┘                   └─────────────────┘                    └────────┬────────┘
                                                                                  │
                                                                        website_plan
                                                                                  │
                    ┌─────────────────────────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │           Section Agents (parallel)               │
    │  hero | about | skills | projects | experience    │
    └───────────────────────┬───────────────────────────┘
                            │
                   sections_content
                            │
                            ▼
                ┌───────────────────────┐
                │  frontend_generator   │
                └───────────┬───────────┘
                            │
                    generated_files
                            │
                            ▼
                ┌───────────────────────┐      ◄──┐
                │      validator        │ ────────┤ retry loop
                └───────────┬───────────┘ ────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   final_assembler     │
                └───────────┬───────────┘
                            │
                            ▼
                    output_path, zip_path
```

---

## Quick Reference: What Imports What

| File | Key Imports |
|------|-------------|
| `app.py` | `core.state`, `core.graph`, `services.resume_parser`, `utils.helpers` |
| `graph.py` | ALL agent nodes, `core.routing`, `core.state` |
| `routing.py` | `core.state` |
| `resume_parser_node.py` | `core.llm_config`, `core.prompts`, `utils.text_cleaner` |
| `website_planner_node.py` | `core.llm_config`, `core.prompts`, `utils.helpers` |
| `*_section_agent.py` | `core.llm_config`, `core.prompts`, `core.state` |
| `frontend_generator.py` | `core.llm_config`, `core.prompts`, `core.state`, `utils.helpers` |
| `validator_agent.py` | `core.llm_config`, `core.prompts`, `core.state`, `utils.helpers` |
| `final_assembler.py` | `services.file_service`, `services.preview_service`, `utils.file_utils` |
