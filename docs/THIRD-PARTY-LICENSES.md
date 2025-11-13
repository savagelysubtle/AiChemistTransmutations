# Third-Party Software Licenses and Attributions

AiChemist Transmutation Codex bundles various third-party software components and external tools. This document provides information about the licenses and usage requirements for all bundled dependencies.

**⚠️ IMPORTANT: By installing this software, you agree to the terms of all licenses listed below.**

---

## 📋 Table of Contents

1. [Bundled External Dependencies](#bundled-external-dependencies)
2. [Python Dependencies](#python-dependencies)
3. [JavaScript/Node Dependencies](#javascriptnode-dependencies)
4. [License Compatibility](#license-compatibility)
5. [Important Legal Notices](#important-legal-notices)

---

## 🔧 Bundled External Dependencies

These tools are **INCLUDED** in the installer. You automatically accept their licenses by installing this software.

### 1. **Tesseract OCR**
- **Purpose**: Optical Character Recognition for PDF text extraction
- **License**: Apache License 2.0
- **Copyright**: Copyright 2006-2024 Google Inc.
- **Homepage**: https://github.com/tesseract-ocr/tesseract
- **License Text**: https://www.apache.org/licenses/LICENSE-2.0
- **Compatibility**: ✅ Compatible with Apache 2.0
- **Bundled Location**: `C:\Program Files\AiChemist Transmutation Codex\external\tesseract\`

**License Summary**: Freely usable for commercial and non-commercial purposes. Source code available at GitHub.

### 2. **Ghostscript**
- **Purpose**: PostScript/PDF processing and rendering
- **License**: GNU Affero General Public License v3.0 (AGPL v3)
- **Copyright**: Copyright (C) 2001-2024 Artifex Software, Inc.
- **Homepage**: https://www.ghostscript.com/
- **License Text**: https://www.gnu.org/licenses/agpl-3.0.html
- **Commercial License**: https://www.artifex.com/licensing/
- **Bundled Location**: `C:\Program Files\AiChemist Transmutation Codex\external\ghostscript\`

**⚠️ IMPORTANT AGPL v3 REQUIREMENTS:**

This software bundles Ghostscript under the AGPL v3 license, which requires:

1. **Source Code Availability**: The complete source code for Ghostscript (and any modifications) must be available.
   - **Ghostscript source**: https://ghostscript.com/releases/gsdnld.html
   - **Our modifications**: None (we use Ghostscript unmodified)

2. **Network Use = Distribution**: If you use this software over a network (SaaS), you must provide source code to users.

3. **License Preservation**: You must retain all license notices and provide AGPL v3 text.

**Commercial Licensing Option**: For commercial use without AGPL obligations, purchase a commercial license from Artifex Software: https://www.artifex.com/licensing/

### 3. **Pandoc**
- **Purpose**: Universal document converter
- **License**: GNU General Public License v2.0 or later (GPL v2+)
- **Copyright**: Copyright (C) 2006-2024 John MacFarlane
- **Homepage**: https://pandoc.org/
- **License Text**: https://www.gnu.org/licenses/gpl-2.0.html
- **Bundled Location**: `C:\Program Files\AiChemist Transmutation Codex\external\pandoc\`

**⚠️ IMPORTANT GPL v2 REQUIREMENTS:**

This software bundles Pandoc under the GPL v2 license, which requires:

1. **Source Code Availability**: The complete source code for Pandoc must be available.
   - **Pandoc source**: https://github.com/jgm/pandoc
   - **Our modifications**: None (we use Pandoc unmodified)

2. **License Preservation**: You must retain all license notices and provide GPL text.

3. **Derivative Works**: Any modifications to Pandoc must be released under GPL v2+.

**Source Code**: Available at https://github.com/jgm/pandoc

### 4. **LibreOffice (via unoserver)**
- **Purpose**: Advanced document conversions (DOCX, XLSX, PPTX)
- **License**: Mozilla Public License v2.0 (MPL 2.0)
- **Copyright**: Copyright 2000-2024 LibreOffice contributors and The Document Foundation
- **Homepage**: https://www.libreoffice.org/
- **License Text**: https://www.mozilla.org/en-US/MPL/2.0/
- **Bundled Location**: `C:\Program Files\AiChemist Transmutation Codex\external\libreoffice\`

**License Summary**: MPL 2.0 is a file-level copyleft license. Source modifications must be shared, but larger works can remain proprietary.

**Source Code**: Available at https://www.libreoffice.org/about-us/source-code/

---

## 🐍 Python Dependencies

These are bundled in the application. All are compatible with Apache 2.0 distribution.

### Core Conversion Libraries

| Package | License | Purpose | Source Code |
|---------|---------|---------|-------------|
| PyPDF2 | BSD 3-Clause | PDF manipulation | https://github.com/py-pdf/pypdf |
| PyMuPDF (fitz) | AGPL v3* | PDF processing | https://github.com/pymupdf/PyMuPDF |
| pypandoc | MIT | Pandoc wrapper | https://github.com/NicklasTegner/pypandoc |
| python-docx | MIT | DOCX creation | https://github.com/python-openxml/python-docx |
| mammoth | BSD 2-Clause | DOCX to HTML | https://github.com/mwilliamson/python-mammoth |
| reportlab | BSD 3-Clause | PDF generation | https://hg.reportlab.com/hg-public/reportlab |
| fpdf2 | LGPL v3 | PDF creation | https://github.com/py-pdf/fpdf2 |
| weasyprint | BSD 3-Clause | HTML to PDF | https://github.com/Kozea/WeasyPrint |
| markdown | BSD 3-Clause | Markdown processing | https://github.com/Python-Markdown/markdown |
| beautifulsoup4 | MIT | HTML parsing | https://www.crummy.com/software/BeautifulSoup/ |
| lxml | BSD 3-Clause | XML processing | https://github.com/lxml/lxml |
| Pillow (PIL) | HPND License | Image processing | https://github.com/python-pillow/Pillow |
| pytesseract | Apache 2.0 | Tesseract wrapper | https://github.com/madmaze/pytesseract |
| ocrmypdf | MPL 2.0 | PDF OCR | https://github.com/ocrmypdf/OCRmyPDF |
| pikepdf | MPL 2.0 | Advanced PDF ops | https://github.com/pikepdf/pikepdf |
| pdfminer.six | MIT | PDF text extraction | https://github.com/pdfminer/pdfminer.six |
| pdf2image | MIT | PDF to images | https://github.com/Belval/pdf2image |
| opencv-python | MIT | Computer vision | https://github.com/opencv/opencv-python |
| numpy | BSD 3-Clause | Numerical computing | https://github.com/numpy/numpy |
| pandas | BSD 3-Clause | Data processing | https://github.com/pandas-dev/pandas |
| openpyxl | MIT | Excel files | https://foss.heptapod.net/openpyxl/openpyxl |
| python-pptx | MIT | PowerPoint files | https://github.com/scanny/python-pptx |
| ebooklib | AGPL v3* | EPUB support | https://github.com/aerkalov/ebooklib |

**Important Notes:**

**PyMuPDF (fitz):**
- Licensed under AGPL v3 (bundled under open source terms)
- ⚠️ Source code available at: https://github.com/pymupdf/PyMuPDF
- We use PyMuPDF unmodified (no custom modifications)
- For commercial distribution without AGPL obligations, consider purchasing commercial license from PyMuPDF

**ebooklib:**
- Licensed under AGPL v3 (bundled under open source terms)
- Source code available at: https://github.com/aerkalov/ebooklib
- Used only for EPUB conversions
- We use ebooklib unmodified

### Utility Libraries

| Package | License | Purpose | Source Code |
|---------|---------|---------|-------------|
| PyYAML | MIT | Configuration files | https://github.com/yaml/pyyaml |
| python-dotenv | BSD 3-Clause | Environment variables | https://github.com/theskumar/python-dotenv |
| requests | Apache 2.0 | HTTP requests | https://github.com/psf/requests |
| flask | BSD 3-Clause | Webhook server | https://github.com/pallets/flask |
| cryptography | Apache 2.0 / BSD | Encryption | https://github.com/pyca/cryptography |
| supabase | MIT | Database client | https://github.com/supabase-community/supabase-py |
| psutil | BSD 3-Clause | System utilities | https://github.com/giampaolo/psutil |

All utility libraries are ✅ **fully compatible** with Apache 2.0 distribution.

---

## 🌐 JavaScript/Node Dependencies

These are bundled in the Electron app. All are compatible with Apache 2.0.

### Core Framework

| Package | License | Purpose | Source Code |
|---------|---------|---------|-------------|
| Electron | MIT | Desktop framework | https://github.com/electron/electron |
| React | MIT | UI framework | https://github.com/facebook/react |
| React DOM | MIT | React rendering | https://github.com/facebook/react |
| Vite | MIT | Build tool | https://github.com/vitejs/vite |
| TypeScript | Apache 2.0 | Language | https://github.com/microsoft/TypeScript |

### UI Libraries

| Package | License | Purpose | Source Code |
|---------|---------|---------|-------------|
| TailwindCSS | MIT | CSS framework | https://github.com/tailwindlabs/tailwindcss |
| lucide-react | ISC | Icon library | https://github.com/lucide-icons/lucide |
| clsx | MIT | Class utilities | https://github.com/lukeed/clsx |
| tailwind-merge | MIT | CSS utilities | https://github.com/dcastil/tailwind-merge |

All JavaScript dependencies are ✅ **fully compatible** with Apache 2.0 distribution.

---

## ⚖️ License Compatibility

### ✅ **Compatible Licenses** (Freely Bundled)

- **MIT License**: Most permissive, allows everything
- **BSD 2-Clause / 3-Clause**: Very permissive, attribution required
- **Apache 2.0**: Same as our license
- **ISC License**: Similar to MIT
- **MPL 2.0**: File-level copyleft, compatible when used as library
- **HPND**: Very permissive

### ⚠️ **Copyleft Licenses** (Bundled with Source Availability)

#### **AGPL v3** (Ghostscript, PyMuPDF, ebooklib)
- **Requirement**: Source code must be available
- **Our Compliance**:
  - All source code available at: https://github.com/savagelysubtle/AiChemistTransmutations
  - Ghostscript source: https://ghostscript.com/releases/gsdnld.html
  - PyMuPDF source: https://github.com/pymupdf/PyMuPDF
  - ebooklib source: https://github.com/aerkalov/ebooklib
- **No Modifications**: We use all AGPL components unmodified

#### **GPL v2+** (Pandoc)
- **Requirement**: Source code must be available
- **Our Compliance**:
  - Pandoc source: https://github.com/jgm/pandoc
  - We use Pandoc unmodified (command-line invocation only)

#### **LGPL v3** (fpdf2)
- **Requirement**: Dynamic linking allowed, modifications must be shared
- **Our Compliance**: Used as Python library (dynamic linking), no modifications

---

## 📜 Important Legal Notices

### **AGPL v3 and GPL Compliance Statement**

This software bundles components licensed under AGPL v3 and GPL v2+:

1. **Source Code Availability**: All source code (including AGPL/GPL components) is freely available:
   - **AiChemist Codex**: https://github.com/savagelysubtle/AiChemistTransmutations
   - **Ghostscript**: https://ghostscript.com/releases/gsdnld.html
   - **Pandoc**: https://github.com/jgm/pandoc
   - **PyMuPDF**: https://github.com/pymupdf/PyMuPDF
   - **ebooklib**: https://github.com/aerkalov/ebooklib

2. **No Modifications**: We use all GPL/AGPL components in their original, unmodified form.

3. **License Texts**: Full license texts are included in:
   - This document (links above)
   - Installation directory: `C:\Program Files\AiChemist Transmutation Codex\licenses\`

4. **Network Use**: If you provide this software as a service over a network (SaaS), you MUST provide the source code to your users under AGPL v3 terms.

### **Commercial Ghostscript Licensing**

Ghostscript is licensed under AGPL v3 in this distribution. For commercial use without AGPL obligations:

- **Purchase a commercial license from**: Artifex Software, Inc.
- **Website**: https://www.artifex.com/licensing/
- **Contact**: ghostscript-sales@artifex.com

Our distribution is under AGPL v3, which is suitable for:
- ✅ Personal use
- ✅ Internal business use (if source provided to employees)
- ✅ Open source distribution
- ⚠️ Commercial SaaS (requires source code disclosure to users)

### **For End Users**

By installing this software, you acknowledge and agree to:

1. **License Terms**: All third-party licenses listed in this document
2. **Source Availability**: All AGPL/GPL source code is available at the links above
3. **No Warranty**: Software provided AS-IS without warranty
4. **AGPL/GPL Compliance**: If you redistribute or provide as network service, you must comply with AGPL/GPL terms

### **For Developers/Redistributors**

If you redistribute this software:

1. **Include This File**: `THIRD-PARTY-LICENSES.md` must be included
2. **Include Main License**: Apache 2.0 `LICENSE` file must be included
3. **Retain Copyrights**: All copyright notices must be preserved
4. **Provide Sources**: Links to all source code must be provided
5. **AGPL/GPL Compliance**:
   - Provide source code for AGPL/GPL components
   - If you modify AGPL/GPL components, your modifications must also be AGPL/GPL
   - Network use = distribution (must provide source to users)

### **Source Code Locations**

**Main Project:**
- https://github.com/savagelysubtle/AiChemistTransmutations

**AGPL/GPL Components:**
- Ghostscript: https://ghostscript.com/releases/gsdnld.html
- Pandoc: https://github.com/jgm/pandoc
- PyMuPDF: https://github.com/pymupdf/PyMuPDF
- ebooklib: https://github.com/aerkalov/ebooklib

**Other Dependencies:**
- See individual package links in tables above
- Python packages: https://pypi.org/project/[package-name]/
- JavaScript packages: https://npmjs.com/package/[package-name]

---

## 🔗 Full License Texts

Full license texts are available:

1. **In Installation Directory**: `C:\Program Files\AiChemist Transmutation Codex\licenses\`
2. **Online**:
   - Apache 2.0: https://www.apache.org/licenses/LICENSE-2.0
   - AGPL v3: https://www.gnu.org/licenses/agpl-3.0.html
   - GPL v2: https://www.gnu.org/licenses/gpl-2.0.html
   - MPL 2.0: https://www.mozilla.org/en-US/MPL/2.0/
   - MIT: https://opensource.org/licenses/MIT
   - BSD: https://opensource.org/licenses/BSD-3-Clause
3. **Individual Component Licenses**: See source code repositories linked above

---

## 📞 Contact

For license questions or concerns:

- **Email**: support@aichemist.app
- **GitHub Issues**: https://github.com/savagelysubtle/AiChemistTransmutations/issues
- **Website**: https://aichemist.app

For commercial Ghostscript licensing:
- **Email**: ghostscript-sales@artifex.com
- **Website**: https://www.artifex.com/licensing/

---

## ⚠️ Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

All third-party software is provided AS-IS under their respective licenses. The authors of AiChemist Transmutation Codex provide this software in compliance with all applicable open source licenses (AGPL v3, GPL v2+, Apache 2.0, MIT, BSD, MPL 2.0, etc.).

**BY INSTALLING THIS SOFTWARE, YOU AGREE TO ALL TERMS AND CONDITIONS LISTED ABOVE.**

---

**Last Updated**: November 13, 2025
**Document Version**: 2.0
**Software Version**: 1.1.0
**License Compliance**: AGPL v3, GPL v2+, Apache 2.0, MIT, BSD, MPL 2.0
