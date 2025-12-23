"""Utils module initialization for Portfolio Builder."""

from .text_cleaner import (
    clean_resume_text,
    extract_urls,
    extract_phone,
    normalize_skills,
    categorize_skills,
    extract_name
)

from .file_utils import (
    ensure_storage_dirs,
    get_project_path,
    create_project_structure,
    write_file,
    read_file,
    create_zip,
    cleanup_project,
    cleanup_old_files,
    save_upload,
    is_valid_resume_file,
    list_project_files
)

from .helpers import (
    generate_project_id,
    safe_json_parse,
    format_component_name,
    format_filename,
    truncate_text,
    extract_code_from_response,
    slugify,
    get_section_order,
    validate_color_hex,
    ensure_hex_color,
    merge_dicts
)

__all__ = [
    # Text cleaner
    "clean_resume_text",
    "extract_urls",
    "extract_phone",
    "normalize_skills",
    "categorize_skills",
    "extract_name",
    # File utils
    "ensure_storage_dirs",
    "get_project_path",
    "create_project_structure",
    "write_file",
    "read_file",
    "create_zip",
    "cleanup_project",
    "cleanup_old_files",
    "save_upload",
    "is_valid_resume_file",
    "list_project_files",
    # Helpers
    "generate_project_id",
    "safe_json_parse",
    "format_component_name",
    "format_filename",
    "truncate_text",
    "extract_code_from_response",
    "slugify",
    "get_section_order",
    "validate_color_hex",
    "ensure_hex_color",
    "merge_dicts",
]
