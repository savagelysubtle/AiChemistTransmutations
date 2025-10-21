#!/usr/bin/env python
"""Script to add licensing feature gates to all paid converters.

This script automatically adds the necessary licensing imports and checks
to all converter files that don't have them yet.
"""

from pathlib import Path
import re


# Converters that need licensing (all except markdown/to_pdf.py which is free tier)
CONVERTERS_TO_UPDATE = [
    "src/transmutation_codex/plugins/pdf/to_editable_pdf.py",
    "src/transmutation_codex/plugins/docx/to_markdown.py",
    "src/transmutation_codex/plugins/docx/to_pdf.py",
    "src/transmutation_codex/plugins/html/to_pdf.py",
    "src/transmutation_codex/plugins/txt/to_pdf.py",
    "src/transmutation_codex/plugins/markdown/to_docx.py",
    "src/transmutation_codex/plugins/markdown/to_html.py",
]

def add_licensing_imports(content: str) -> str:
    """Add licensing imports to the file."""
    # Find the transmutation_codex.core import block
    pattern = r'from transmutation_codex\.core import \((.*?)\)'

    def replacement(match):
        imports = match.group(1)
        # Add licensing imports if not present
        if 'check_feature_access' not in imports:
            imports = imports.strip()
            # Add the licensing imports
            imports += ',\n    check_feature_access,\n    check_file_size_limit,\n    record_conversion_attempt,'
        return f'from transmutation_codex.core import ({imports})'

    # Try multi-line import
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # If not found, try single-line import
    if 'check_feature_access' not in content:
        pattern_single = r'from transmutation_codex\.core import ([^\n]+)'
        def replacement_single(match):
            imports = match.group(1)
            if imports.endswith(','):
                imports = imports.rstrip(',')
            imports += ',\n    check_feature_access,\n    check_file_size_limit,\n    record_conversion_attempt,'
            return f'from transmutation_codex.core import {imports}'
        content = re.sub(pattern_single, replacement_single, content)

    return content


def add_feature_check(content: str, converter_name: str) -> str:
    """Add feature access check and file size check at start of try block."""
    # Find the first `try:` block after the function definition
    # Look for pattern: "    try:" (4 spaces indent)
    pattern = r'(\n    try:\n)(        (?!.*check_feature_access))'

    license_check = f'''        # License validation and feature gating ({converter_name} is paid-only)
        check_feature_access("{converter_name}")

        # Convert to Path for validation
        input_path = Path(input_path).resolve()

        # Check file size limit
        check_file_size_limit(str(input_path))

'''

    replacement = r'\1' + license_check + r'\2'
    content = re.sub(pattern, replacement, content, count=1)

    return content


def add_conversion_tracking(content: str, converter_name: str) -> str:
    """Add conversion tracking before complete_operation."""
    #  Look for complete_operation calls and add tracking before them
    pattern = r'(\n        )(complete_operation\(operation, success=True\))'

    tracking_code = f'''# Record conversion for trial tracking
        record_conversion_attempt(
            converter_name="{converter_name}",
            input_file=str(input_path),
            output_file=str(output_path),
            success=True,
        )

        '''

    replacement = r'\1' + tracking_code + r'\2'
    content = re.sub(pattern, replacement, content)

    return content


def get_converter_name(file_path: str) -> str:
    """Extract converter name from file path."""
    # pdf/to_markdown.py -> pdf2md
    # markdown/to_pdf.py -> md2pdf
    # etc.
    parts = file_path.split('/')
    source_format = parts[-2]  # e.g., 'pdf', 'markdown'
    target_file = parts[-1]     # e.g., 'to_markdown.py'
    target_format = target_file.replace('to_', '').replace('.py', '')

    # Create short names
    format_map = {
        'markdown': 'md',
        'document': 'doc',
        'editable_pdf': 'editable',
    }

    source = format_map.get(source_format, source_format)
    target = format_map.get(target_format, target_format)

    return f"{source}2{target}"


def process_converter(file_path: Path, converter_name: str):
    """Process a single converter file."""
    print(f"Processing {file_path}...")

    if not file_path.exists():
        print(f"  ⚠ File not found: {file_path}")
        return False

    content = file_path.read_text(encoding='utf-8')

    # Check if already has licensing
    if 'check_feature_access' in content:
        print(f"  ✓ Already has licensing")
        return True

    # Add imports
    content = add_licensing_imports(content)

    # Add feature check
    content = add_feature_check(content, converter_name)

    # Add conversion tracking
    content = add_conversion_tracking(content, converter_name)

    # Write back
    file_path.write_text(content, encoding='utf-8')
    print(f"  ✅ Updated successfully")
    return True


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    print("🔒 Adding licensing to paid converters...\n")

    success_count = 0
    for converter_path in CONVERTERS_TO_UPDATE:
        full_path = project_root / converter_path
        converter_name = get_converter_name(converter_path)

        if process_converter(full_path, converter_name):
            success_count += 1

    print(f"\n✅ Successfully updated {success_count}/{len(CONVERTERS_TO_UPDATE)} converters")


if __name__ == "__main__":
    main()
