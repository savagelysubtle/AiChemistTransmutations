"""Create test EPUB files for converter testing.

This script generates various EPUB files with different characteristics
to test the EPUB conversion functionality.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from datetime import datetime

    from ebooklib import epub
except ImportError:
    print("Error: ebooklib not installed")
    print("Please install: pip install ebooklib")
    sys.exit(1)


def create_simple_epub():
    """Create a simple EPUB with basic text content."""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("test-epub-simple-001")
    book.set_title("Simple Test EPUB")
    book.set_language("en")
    book.add_author("Test Author")

    # Create chapter
    c1 = epub.EpubHtml(title="Chapter 1", file_name="chap_01.xhtml", lang="en")
    c1.content = """
    <h1>Chapter 1: Introduction</h1>
    <p>This is a simple test EPUB file created for testing the EPUB converters.</p>
    <p>It contains basic HTML formatting including:</p>
    <ul>
        <li>Paragraphs</li>
        <li>Lists</li>
        <li>Headings</li>
    </ul>
    <p><strong>Bold text</strong> and <em>italic text</em> are supported.</p>
    """

    c2 = epub.EpubHtml(title="Chapter 2", file_name="chap_02.xhtml", lang="en")
    c2.content = """
    <h1>Chapter 2: Content</h1>
    <p>This chapter contains some sample content to test multi-chapter EPUB files.</p>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
    """

    # Add chapters
    book.add_item(c1)
    book.add_item(c2)

    # Define Table of Contents
    book.toc = (c1, c2)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define spine
    book.spine = ["nav", c1, c2]

    # Write EPUB file
    output_path = Path(__file__).parent / "test_epub_simple.epub"
    epub.write_epub(str(output_path), book, {})
    print(f"✓ Created: {output_path.name}")


def create_complex_epub():
    """Create a complex EPUB with images, styles, and multiple chapters."""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("test-epub-complex-001")
    book.set_title("Complex Test EPUB: A Comprehensive Example")
    book.set_language("en")
    book.add_author("John Doe")
    book.add_author("Jane Smith")
    book.add_metadata(
        "DC",
        "description",
        "A complex EPUB file for testing advanced conversion features",
    )
    book.add_metadata("DC", "publisher", "AiChemist Test Suite")
    book.add_metadata("DC", "date", datetime.now().strftime("%Y-%m-%d"))

    # Add CSS style
    style = """
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        margin: 2em;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5em;
    }
    h2 {
        color: #34495e;
        margin-top: 1.5em;
    }
    .quote {
        font-style: italic;
        border-left: 3px solid #3498db;
        padding-left: 1em;
        margin: 1em 0;
    }
    .code {
        background-color: #f4f4f4;
        border: 1px solid #ddd;
        border-radius: 3px;
        font-family: monospace;
        padding: 1em;
        overflow-x: auto;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #3498db;
        color: white;
    }
    """

    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style
    )
    book.add_item(nav_css)

    # Create chapters with rich content
    intro = epub.EpubHtml(title="Introduction", file_name="intro.xhtml", lang="en")
    intro.content = """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/nav.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>Introduction</h1>
        <p>Welcome to this comprehensive test EPUB document. This file is designed to
        test various features of EPUB converters including:</p>
        <ul>
            <li>Rich HTML formatting</li>
            <li>CSS styling</li>
            <li>Multiple chapters and sections</li>
            <li>Tables and code blocks</li>
            <li>Lists and quotes</li>
        </ul>
        <div class="quote">
            <p>"Testing is an essential part of software development. Comprehensive
            test files ensure robust conversion capabilities." - Anonymous Developer</p>
        </div>
    </body>
    </html>
    """
    intro.add_item(nav_css)

    chapter1 = epub.EpubHtml(
        title="Chapter 1: Formatting", file_name="chap_01.xhtml", lang="en"
    )
    chapter1.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/nav.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>Chapter 1: Text Formatting</h1>

        <h2>Basic Formatting</h2>
        <p>This paragraph demonstrates <strong>bold text</strong>, <em>italic text</em>,
        and <u>underlined text</u>. You can also have <code>inline code</code>.</p>

        <h2>Lists</h2>
        <p>Ordered list:</p>
        <ol>
            <li>First item</li>
            <li>Second item</li>
            <li>Third item with <strong>formatting</strong></li>
        </ol>

        <p>Unordered list:</p>
        <ul>
            <li>Apple</li>
            <li>Banana</li>
            <li>Cherry</li>
        </ul>

        <h2>Code Block</h2>
        <div class="code">
def hello_world():
    """A simple Python function."""
    print("Hello, World!")
    return True
        </div>
    </body>
    </html>
    '''
    chapter1.add_item(nav_css)

    chapter2 = epub.EpubHtml(
        title="Chapter 2: Tables", file_name="chap_02.xhtml", lang="en"
    )
    chapter2.content = """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/nav.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>Chapter 2: Tables and Data</h1>

        <h2>Sample Data Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Converter</th>
                    <th>Input Format</th>
                    <th>Output Format</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>EPUB to PDF</td>
                    <td>.epub</td>
                    <td>.pdf</td>
                    <td>✓ Working</td>
                </tr>
                <tr>
                    <td>EPUB to HTML</td>
                    <td>.epub</td>
                    <td>.html</td>
                    <td>✓ Working</td>
                </tr>
                <tr>
                    <td>EPUB to Markdown</td>
                    <td>.epub</td>
                    <td>.md</td>
                    <td>✓ Working</td>
                </tr>
                <tr>
                    <td>Markdown to EPUB</td>
                    <td>.md</td>
                    <td>.epub</td>
                    <td>✓ Working</td>
                </tr>
            </tbody>
        </table>

        <p>This table demonstrates how tabular data can be embedded in EPUB files
        and properly converted to other formats.</p>
    </body>
    </html>
    """
    chapter2.add_item(nav_css)

    chapter3 = epub.EpubHtml(
        title="Chapter 3: Conclusion", file_name="chap_03.xhtml", lang="en"
    )
    chapter3.content = """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/nav.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>Chapter 3: Conclusion</h1>

        <p>This test EPUB file has demonstrated various features that should be
        properly handled during conversion:</p>

        <ul>
            <li>Multiple chapters with navigation</li>
            <li>Rich HTML formatting (bold, italic, underline)</li>
            <li>CSS styling for consistent appearance</li>
            <li>Tables with headers and data</li>
            <li>Code blocks and inline code</li>
            <li>Quotes and blockquotes</li>
            <li>Ordered and unordered lists</li>
        </ul>

        <div class="quote">
            <p>The quality of a converter is measured not just by what it converts,
            but by how well it preserves the structure and formatting of the original
            document.</p>
        </div>

        <h2>Final Notes</h2>
        <p>If all these elements are properly converted, the EPUB converter is working
        as expected. Any loss of formatting or structure should be documented and
        addressed.</p>
    </body>
    </html>
    """
    chapter3.add_item(nav_css)

    # Add all chapters
    book.add_item(intro)
    book.add_item(chapter1)
    book.add_item(chapter2)
    book.add_item(chapter3)

    # Define Table of Contents
    book.toc = (
        epub.Link("intro.xhtml", "Introduction", "intro"),
        (epub.Section("Chapters"), (chapter1, chapter2, chapter3)),
    )

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define spine
    book.spine = ["nav", intro, chapter1, chapter2, chapter3]

    # Write EPUB file
    output_path = Path(__file__).parent / "test_epub_complex.epub"
    epub.write_epub(str(output_path), book, {})
    print(f"✓ Created: {output_path.name}")


def create_multilang_epub():
    """Create a multi-language EPUB for testing language support."""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("test-epub-multilang-001")
    book.set_title("Multilingual Test EPUB")
    book.set_language("en")
    book.add_author("International Test Team")

    # English chapter
    c1 = epub.EpubHtml(title="English Chapter", file_name="chap_en.xhtml", lang="en")
    c1.content = """
    <h1>English Chapter</h1>
    <p>This is an English chapter demonstrating basic Latin text.</p>
    <p>The quick brown fox jumps over the lazy dog.</p>
    """

    # Spanish chapter
    c2 = epub.EpubHtml(
        title="Capítulo en Español", file_name="chap_es.xhtml", lang="es"
    )
    c2.content = """
    <h1>Capítulo en Español</h1>
    <p>Este es un capítulo en español para probar el soporte de caracteres especiales.</p>
    <p>¿Cómo estás? ¡Muy bien!</p>
    """

    # French chapter
    c3 = epub.EpubHtml(title="Chapitre Français", file_name="chap_fr.xhtml", lang="fr")
    c3.content = """
    <h1>Chapitre Français</h1>
    <p>Ceci est un chapitre en français pour tester les caractères accentués.</p>
    <p>À bientôt! Ça va très bien.</p>
    """

    # German chapter
    c4 = epub.EpubHtml(title="Deutsches Kapitel", file_name="chap_de.xhtml", lang="de")
    c4.content = """
    <h1>Deutsches Kapitel</h1>
    <p>Dies ist ein deutsches Kapitel zum Testen von Umlauten.</p>
    <p>Äpfel, Öfen, Übung - ß ist auch dabei!</p>
    """

    # Add chapters
    book.add_item(c1)
    book.add_item(c2)
    book.add_item(c3)
    book.add_item(c4)

    # Define Table of Contents
    book.toc = (c1, c2, c3, c4)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define spine
    book.spine = ["nav", c1, c2, c3, c4]

    # Write EPUB file
    output_path = Path(__file__).parent / "test_epub_multilang.epub"
    epub.write_epub(str(output_path), book, {})
    print(f"✓ Created: {output_path.name}")


def create_technical_epub():
    """Create a technical document EPUB with code and formulas."""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier("test-epub-technical-001")
    book.set_title("Technical Documentation Test EPUB")
    book.set_language("en")
    book.add_author("Technical Writer")
    book.add_metadata("DC", "subject", "Programming, Documentation, Testing")

    # Add CSS for code formatting
    code_css = """
    body { font-family: Arial, sans-serif; }
    h1 { color: #2c3e50; }
    .code-block {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-left: 3px solid #4CAF50;
        padding: 15px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        margin: 1em 0;
    }
    .inline-code {
        background-color: #f0f0f0;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: monospace;
    }
    """

    css = epub.EpubItem(
        uid="style_code",
        file_name="style/code.css",
        media_type="text/css",
        content=code_css,
    )
    book.add_item(css)

    # Python chapter
    python_chapter = epub.EpubHtml(
        title="Python Examples", file_name="python.xhtml", lang="en"
    )
    python_chapter.content = '''
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/code.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>Python Code Examples</h1>

        <h2>Hello World</h2>
        <div class="code-block">
def hello_world():
    """Print a greeting message."""
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
        </div>

        <h2>Classes and Objects</h2>
        <div class="code-block">
class DocumentConverter:
    """Convert documents between formats."""

    def __init__(self, input_format, output_format):
        self.input_format = input_format
        self.output_format = output_format

    def convert(self, input_path, output_path):
        """Perform the conversion."""
        print(f"Converting {input_path} to {output_path}")
        return True
        </div>

        <p>To use this class, simply call <span class="inline-code">converter.convert()</span>
        with the appropriate paths.</p>
    </body>
    </html>
    '''
    python_chapter.add_item(css)

    # JavaScript chapter
    js_chapter = epub.EpubHtml(
        title="JavaScript Examples", file_name="javascript.xhtml", lang="en"
    )
    js_chapter.content = """
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link href="../style/code.css" rel="stylesheet" type="text/css"/>
    </head>
    <body>
        <h1>JavaScript Code Examples</h1>

        <h2>Async/Await</h2>
        <div class="code-block">
async function convertDocument(inputPath, outputPath) {
    try {
        const result = await electronAPI.runConversion({
            conversionType: 'epub2pdf',
            inputFiles: [inputPath],
            outputDir: outputPath
        });

        console.log('Conversion successful:', result);
        return result;
    } catch (error) {
        console.error('Conversion failed:', error);
        throw error;
    }
}
        </div>

        <h2>React Component</h2>
        <div class="code-block">
const ConversionButton = ({ onClick, disabled }) => {
    return (
        &lt;button
            onClick={onClick}
            disabled={disabled}
            className="btn-primary"
        &gt;
            Convert Document
        &lt;/button&gt;
    );
};
        </div>
    </body>
    </html>
    """
    js_chapter.add_item(css)

    # Add chapters
    book.add_item(python_chapter)
    book.add_item(js_chapter)

    # Define Table of Contents
    book.toc = (python_chapter, js_chapter)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define spine
    book.spine = ["nav", python_chapter, js_chapter]

    # Write EPUB file
    output_path = Path(__file__).parent / "test_epub_technical.epub"
    epub.write_epub(str(output_path), book, {})
    print(f"✓ Created: {output_path.name}")


def main():
    """Generate all test EPUB files."""
    print("\n=== Creating Test EPUB Files ===\n")

    try:
        create_simple_epub()
        create_complex_epub()
        create_multilang_epub()
        create_technical_epub()

        print("\n✅ All test EPUB files created successfully!")
        print("\nGenerated files:")
        print("  - test_epub_simple.epub      (Basic text and formatting)")
        print("  - test_epub_complex.epub     (Rich content with tables and styles)")
        print("  - test_epub_multilang.epub   (Multi-language content)")
        print("  - test_epub_technical.epub   (Technical documentation with code)")

    except Exception as e:
        print(f"\n❌ Error creating EPUB files: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
