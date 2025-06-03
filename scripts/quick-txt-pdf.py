from pathlib import Path
from fpdf import FPDF
import re

# Load the file
txt_path = Path("vikashloomba-copilot-mcp.txt")
with open(txt_path, "r", encoding="utf-8") as f:
    content = f.read()

# Parse sections based on file dump format
file_blocks = re.split(r"\n=+\nFILE: (.+?)\n=+\n", content)
sections = []
for i in range(1, len(file_blocks), 2):
    filename = file_blocks[i].strip()
    filecontent = file_blocks[i+1].strip()
    sections.append((filename, filecontent))

def clean_text(text: str) -> str:
    # Remove or replace non-latin1 chars
    return ''.join(c if ord(c) < 256 else '?' for c in text)

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=10)

pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Repository: vikashloomba-copilot-mcp", ln=1, align="C")
pdf.set_font("Arial", "", 12)
pdf.cell(0, 10, "Exported as PDF - major files and structure", ln=1, align="C")
pdf.ln(5)

for filename, filecontent in sections:
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 10, f"File: {filename}")
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    max_lines = 70
    lines = filecontent.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["...", "[truncated]"]
    section_text = clean_text("\n".join(lines))
    pdf.multi_cell(0, 5, section_text)

pdf.output("vikashloomba-copilot-mcp-export.pdf")
