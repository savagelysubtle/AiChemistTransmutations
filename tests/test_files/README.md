# Test Files for AiChemist Transmutation Codex

This directory contains comprehensive test files for all premium converters and features.

## File Categories

### Excel/CSV Test Files

- `test_excel_sample.xlsx` - Multi-sheet Excel file with sales, employee, and financial data
- `test_csv_sample.csv` - Simple CSV with basic data structure
- `test_csv_complex.csv` - CSV with special characters and quoted fields
- `create_excel_test.py` - Script to generate Excel test files (requires pandas, openpyxl)

### PowerPoint Test Files

- `test_powerpoint_sample.pptx` - Multi-slide presentation with various content types

### Image Test Files

- `test_image_sample.png` - PNG image for general testing
- `test_image_sample.jpg` - JPEG image for general testing
- `test_image_sample.tiff` - TIFF image for high-quality testing
- `test_image_formats.bmp` - BMP format test image
- `test_image_formats.gif` - GIF format test image
- `test_image_formats.webp` - WebP format test image
- `test_ocr_document.png` - High-resolution scanned document for OCR testing
- `test_ocr_handwritten.jpg` - Handwritten notes for OCR testing

### EPUB Test Files

- `test_epub_sample.epub` - Complete EPUB book with multiple chapters and metadata

### Advanced PDF Test Files

- `test_pdf_multi_page.pdf` - Multi-page PDF for page operations testing
- `test_pdf_with_tables.pdf` - PDF with tables for data extraction testing
- `test_large_document.pdf` - Large PDF for performance testing
- `test_corrupted_document.pdf` - Corrupted PDF for error handling testing
- `test_password_protected.pdf` - Password-protected PDF for security testing

### Batch Processing Test Files

- `batch_test_1.pdf` - PDF for batch conversion testing
- `batch_test_2.docx` - DOCX for batch conversion testing
- `batch_test_3.html` - HTML for batch conversion testing
- `batch_test_4.md` - Markdown for batch conversion testing
- `batch_test_5.txt` - Plain text for batch conversion testing

### Existing Test Files

- `electron_test.*` - Original test files for basic functionality
- `test.html` - HTML test file
- `test.pdf` - PDF test file
- `test.txt` - Text test file
- `test_pagebreak.*` - Page break testing files

## Testing Scenarios

### Excel/CSV Converters

- Multi-sheet Excel to PDF/HTML/Markdown
- CSV to Excel conversion with formatting
- Table extraction from PDF to Excel
- Special character handling in CSV
- Large dataset processing

### PowerPoint Converters

- Multi-slide presentation conversion
- Image extraction from slides
- Text and formatting preservation
- Slide layout maintenance

### Image Converters

- Format conversion (PNG, JPEG, TIFF, BMP, GIF, WebP)
- OCR text extraction
- Image to PDF conversion
- Quality preservation
- Metadata handling

### EPUB Converters

- EPUB to PDF/HTML/Markdown conversion
- Markdown/DOCX/HTML to EPUB creation
- Metadata preservation
- Chapter structure maintenance
- Image and styling handling

### Advanced PDF Operations

- Page splitting and merging
- PDF compression optimization
- Password protection and encryption
- Watermark addition
- Page rotation and removal
- OCR layer addition
- Table extraction

### Batch Processing

- Multiple format conversion
- Progress tracking
- Error handling
- Performance optimization
- Memory management

## Usage

These test files are designed to:

1. Verify converter functionality
2. Test edge cases and error handling
3. Validate performance with different file sizes
4. Ensure quality preservation across formats
5. Test batch processing capabilities

## Dependencies

Some test file generation requires:

- `pandas` - For CSV/Excel data manipulation
- `openpyxl` - For Excel file creation
- `python-pptx` - For PowerPoint file creation
- `Pillow` - For image file creation
- `ebooklib` - For EPUB file creation

## Notes

- Binary files are represented as text descriptions for version control
- Actual binary files should be generated using the provided scripts
- Test files cover both success and failure scenarios
- Files are designed to test specific converter features and edge cases
