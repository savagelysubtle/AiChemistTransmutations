# AiChemist Transmutation Codex - Documentation Directory

This directory contains all project documentation, including Sphinx-generated API docs, setup guides, troubleshooting documentation, and implementation records.

## 📁 Directory Structure

```
docs/
├── README.md                        # This file
├── build_docs.py                    # Build Sphinx documentation
├── generate_api_docs.py             # Generate API docs from code
├── make.bat / Makefile              # Sphinx build commands
│
├── 📄 Active Documentation (Root)
│   ├── DEPLOYMENT_CHECKLIST.md     # Production deployment checklist
│   ├── PRODUCTION_DEPLOYMENT.md    # Production deployment guide
│   └── SUPABASE_INTEGRATION.md     # Supabase integration guide
│
├── ✅ completed/                    # Implementation History
│   ├── CONTINUATION_FROM_AUTH.md
│   ├── IMPLEMENTATION_SUMMARY_PATH.md
│   ├── LICENSING_IMPLEMENTATION_COMPLETE.md
│   ├── LICENSING_IMPLEMENTATION_SUMMARY.md
│   ├── LICENSING_SETUP_COMPLETE.md
│   ├── PRODUCTION_SETUP.md
│   └── SUPABASE_SETUP_COMPLETE.md
│
├── 📚 guides/                       # Setup & Bundling Guides
│   ├── AUTO_PATH_CONFIGURATION.md
│   ├── BUNDLING_TESSERACT.md
│   ├── GHOSTSCRIPT_BUNDLING.md
│   ├── GHOSTSCRIPT_BUNDLING_INSTALLER.md
│   ├── MIKTEX_BUNDLING.md
│   ├── PANDOC_BUNDLING.md
│   └── TESSERACT_CONFIGURATION.md
│
├── 🔧 troubleshooting/              # Problem-Solving Docs
│   ├── AUTO_RETRY_FORCE_OCR.md
│   ├── DOCX2PDF_ENGINE_FIX.md
│   └── TROUBLESHOOTING_PATH.md
│
├── 🗺️ plans/                         # Future Development
│   └── pdf_editor_development_plan.rst
│
├── 📖 source/                        # Sphinx Source (reStructuredText)
│   ├── conf.py                      # Sphinx configuration
│   ├── index.rst                    # Main documentation index
│   ├── installation.rst
│   ├── usage.rst
│   ├── contributing.rst
│   ├── changelog.rst
│   │
│   ├── api/                         # Auto-generated API docs
│   ├── architecture/                # Architecture documentation
│   ├── development/                 # Development guides
│   ├── usage/                       # User guides
│   └── _static/                     # CSS, images, assets
│       └── custom.css
│
└── 🏗️ build/                         # Generated Documentation (gitignored)
    ├── html/                        # HTML documentation output
    └── doctrees/                    # Sphinx cache
```

## 🚀 Quick Start

### Building Documentation

```bash
# Build all documentation (API + HTML)
python docs/build_docs.py

# Or use Make
cd docs/
make html          # Unix/Linux/macOS
.\make.bat html    # Windows

# View generated docs
# Open: docs/build/html/index.html
```

### Generating API Documentation Only

```bash
python docs/generate_api_docs.py
```

## 📚 Documentation Categories

### Active Documentation (Root Level)

**Purpose**: Currently relevant, actively maintained documentation
**Location**: `docs/` (root)

#### DEPLOYMENT_CHECKLIST.md

Complete checklist for production deployment

- Pre-deployment verification
- Deployment steps
- Post-deployment validation
- Rollback procedures

#### PRODUCTION_DEPLOYMENT.md

Comprehensive production deployment guide

- Environment setup
- Configuration
- Deployment process
- Monitoring and maintenance

#### SUPABASE_INTEGRATION.md

Supabase licensing backend integration

- Setup instructions
- API usage
- Authentication
- Database schema

### Completed Documentation (`completed/`)

**Purpose**: Implementation history and completion records
**Location**: `docs/completed/`

These documents provide an audit trail of completed implementations:

- Implementation summaries
- Setup completion records
- Session continuation notes
- Historical reference

**Never Delete**: Kept for project history and reference

### Setup & Bundling Guides (`guides/`)

**Purpose**: External dependency setup and bundling instructions
**Location**: `docs/guides/`

#### Bundling Guides

- **BUNDLING_TESSERACT.md** - Bundle Tesseract OCR
- **GHOSTSCRIPT_BUNDLING.md** - Bundle Ghostscript
- **PANDOC_BUNDLING.md** - Bundle Pandoc
- **MIKTEX_BUNDLING.md** - Bundle MiKTeX

#### Configuration Guides

- **AUTO_PATH_CONFIGURATION.md** - Automatic PATH configuration
- **TESSERACT_CONFIGURATION.md** - Tesseract setup and config
- **GHOSTSCRIPT_BUNDLING_INSTALLER.md** - Ghostscript installer

### Troubleshooting Documentation (`troubleshooting/`)

**Purpose**: Problem-solving guides and fixes
**Location**: `docs/troubleshooting/`

- **TROUBLESHOOTING_PATH.md** - PATH-related issues
- **AUTO_RETRY_FORCE_OCR.md** - OCR retry mechanisms
- **DOCX2PDF_ENGINE_FIX.md** - DOCX to PDF engine issues

### Future Plans (`plans/`)

**Purpose**: Roadmaps and future development proposals
**Location**: `docs/plans/`
**Format**: `.rst` (reStructuredText)

- **pdf_editor_development_plan.rst** - PDF editor feature plan

### Sphinx Documentation (`source/`)

**Purpose**: Generated HTML documentation
**Location**: `docs/source/`
**Format**: `.rst` (reStructuredText) ONLY

#### Sphinx Subdirectories

- **`api/`** - Auto-generated from Python docstrings (DO NOT EDIT MANUALLY)
- **`architecture/`** - Architecture decisions, design patterns
- **`development/`** - Development guides, research notes
- **`usage/`** - User guides, examples, tutorials
- **`_static/`** - CSS, images, static assets

## 📝 File Format Standards

### Use reStructuredText (.rst)

**Required For**:

- All Sphinx documentation (`docs/source/`)
- Architecture documentation
- Development guides
- API documentation

**Example**:

```rst
My Document Title
=================

Section Heading
---------------

This is a paragraph with **bold** and *italic* text.

.. code-block:: python

   def example():
       return "Hello, World!"

.. note::
   This is an important note.
```

### Use Markdown (.md)

**Allowed For**:

- Root-level documentation
- Completion records (`completed/`)
- Setup guides (`guides/`)
- Troubleshooting docs (`troubleshooting/`)

**Never Use For**:

- Sphinx source files (`source/` must be .rst)

## 🛠️ Sphinx Configuration

### Main Configuration

- **File**: `docs/source/conf.py`
- **Theme**: Read the Docs (sphinx_rtd_theme)
- **Extensions**:
  - `sphinx.ext.autodoc` - Auto-generate API docs
  - `sphinx.ext.napoleon` - Google/NumPy docstring support
  - `sphinx.ext.viewcode` - Add links to source code
  - `sphinx_design` - UI components (dropdowns, tabs, cards)
  - `sphinx_copybutton` - Copy buttons for code blocks

### Custom Styling

- **File**: `docs/source/_static/custom.css`
- **Features**:
  - Lime green theme (brand colors)
  - Dark background for code blocks
  - Custom admonition styling
  - Monokai syntax highlighting

## 📖 Adding New Documentation

### Quick Guide

```bash
# 1. Determine the correct location
#    - Active guide? → docs/ (root)
#    - Setup/bundling? → docs/guides/
#    - Troubleshooting? → docs/troubleshooting/
#    - Implementation record? → docs/completed/
#    - User guide? → docs/source/usage/

# 2. Choose the correct format
#    - Sphinx docs → .rst
#    - Everything else → .md

# 3. Create the file
touch docs/guides/NEW_GUIDE.md

# 4. Follow the template structure
#    - Overview
#    - Prerequisites
#    - Step-by-step instructions
#    - Verification
#    - Troubleshooting

# 5. Update navigation (if Sphinx)
#    Add to appropriate index.rst

# 6. Build and verify (if Sphinx)
python docs/build_docs.py
```

### Documentation Templates

#### Setup/Installation Guide Template

```markdown
# Tool Installation Guide

## Overview
Brief description of what this tool does and why it's needed.

## Prerequisites
- Requirement 1
- Requirement 2

## Installation Steps

### Step 1: Download
Instructions...

### Step 2: Install
Instructions...

### Step 3: Configure
Instructions...

## Verification
How to verify the installation was successful...

## Troubleshooting

### Issue 1: Problem Description
Solution...

### Issue 2: Problem Description
Solution...

## See Also
- Related documentation
- External references
```

#### Troubleshooting Guide Template

```markdown
# Problem: Issue Description

## Symptoms
- Symptom 1
- Symptom 2
- Error messages

## Cause
Explanation of why this issue occurs...

## Solution

### Method 1: Primary Solution
1. Step 1
2. Step 2

### Method 2: Alternative Solution
1. Step 1
2. Step 2

## Prevention
How to prevent this issue in the future...

## Related Issues
- Link to related problem 1
- Link to related problem 2
```

## 🔧 Sphinx Components

### Dropdowns

```rst
.. dropdown:: Click to expand
   :icon: question-circle
   :color: primary

   Hidden content here.
```

### Code Blocks

```rst
.. code-block:: python
   :caption: Example Code
   :emphasize-lines: 2-3
   :linenos:

   def hello():
       print("Hello")  # This line is highlighted
       return True     # This line too
```

### Admonitions

```rst
.. note::
   Informational note.

.. warning::
   Warning message.

.. tip::
   Helpful tip.
```

See `.cursor/rules/401-sphinx-components-usage.mdc` for more details.

## 📋 Documentation Standards

### Content Requirements

1. **Clear purpose** stated at the beginning
2. **Step-by-step instructions** for procedures
3. **Code examples** where applicable
4. **Screenshots** for GUI procedures
5. **Cross-references** to related docs
6. **Last updated date** for time-sensitive docs

### Writing Style

- ✅ Use imperative mood: "Install...", "Configure..."
- ✅ Use present tense for descriptions
- ✅ Use active voice
- ✅ Keep sentences concise
- ✅ Use bullet points for lists
- ✅ Use numbered lists for sequential steps

### Code Examples

- Always test code examples
- Include full context (imports, setup)
- Add comments for complex operations
- Show expected output

## 🚦 Common Tasks

### Update API Documentation

```bash
# Regenerate API docs after code changes
python docs/generate_api_docs.py

# Rebuild HTML
python docs/build_docs.py
```

### Add a New User Guide

```bash
# 1. Create .rst file
touch docs/source/usage/new_feature.rst

# 2. Add content
# 3. Update docs/source/usage/index.rst
# 4. Build docs
python docs/build_docs.py

# 5. Verify output
# Open: docs/build/html/usage/new_feature.html
```

### Move Implementation to Completed

```bash
# When implementation is finished
mv docs/MY_IMPLEMENTATION.md docs/completed/
```

## ⚠️ Common Mistakes to Avoid

1. ❌ Using `.md` files in `docs/source/` (must be `.rst`)
2. ❌ Not updating navigation when adding new Sphinx docs
3. ❌ Committing `docs/build/` directory (gitignored)
4. ❌ Missing docstrings in Python code (breaks API docs)
5. ❌ Not testing code examples
6. ❌ Leaving implementation summaries in root
7. ❌ Hardcoding file paths (use relative paths)
8. ❌ Not building docs after changes

## 📚 External References

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx Design Components](https://sphinx-design.readthedocs.io/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

## 🎯 Quick Reference

### Where Does This Doc Go?

| Documentation Type | Location | Format | Example |
|--------------------|----------|--------|---------|
| Active deployment guide | `docs/` | .md | DEPLOYMENT_CHECKLIST.md |
| Implementation record | `docs/completed/` | .md | LICENSING_SETUP_COMPLETE.md |
| Setup guide | `docs/guides/` | .md | TESSERACT_CONFIGURATION.md |
| Troubleshooting | `docs/troubleshooting/` | .md | DOCX2PDF_ENGINE_FIX.md |
| Future plan | `docs/plans/` | .rst | pdf_editor_development_plan.rst |
| User guide | `docs/source/usage/` | .rst | pdf_merging.rst |
| API docs | `docs/source/api/` | .rst | Auto-generated |
| Architecture | `docs/source/architecture/` | .rst | design_decisions.rst |

---

**Maintained by**: @savagelysubtle
**Last Updated**: October 2025
**See Also**:

- [.cursor/rules/051-docs-directory-layout.mdc](mdc:.cursor/rules/051-docs-directory-layout.mdc)
- [.cursor/rules/400-documentation-format.mdc](mdc:.cursor/rules/400-documentation-format.mdc)
- [.cursor/rules/401-sphinx-components-usage.mdc](mdc:.cursor/rules/401-sphinx-components-usage.mdc)
