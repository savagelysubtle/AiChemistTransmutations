.. automodule:: aichemist_transmutation_codex
    :members:

PDF Editor Feature Development Plan
===================================

.. contents::
   :local:

Introduction
------------

This document outlines the plan for developing an in-application PDF editor. The editor will allow users to perform basic modifications to PDF documents.
The development will follow the guidelines set forth in the project's architecture and feature development rules, particularly ``8XX-pdf-editing-workflow`` and ``9XX-gui-pdf-editor-template``.

Core Technologies
-----------------

*   **Frontend**: Electron, React, TypeScript, Vite
    *   **PDF Rendering**: ``react-pdf`` (a wrapper for Mozilla's ``PDF.js``)
    *   **PDF Manipulation (Client-Side)**: ``pdf-lib``
    *   **UI Components**: TailwindCSS, Shadcn/UI
*   **Backend (for complex operations, if needed)**: Python 3.13
    *   Communication via ``electron_bridge.py`` following existing JSON-based messaging.
*   **Build & Dependency Management**: UV (Python), npm/yarn (Node.js/Frontend)

Phased Development
------------------

The development will be broken down into the following phases:

Phase 1: Research & Setup
~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Finalize library choices, set up the basic project structure for the editor, and create proof-of-concepts for core interactions.
*   **Tasks**:
    1.  Confirm compatibility and specific versions of ``react-pdf`` and ``pdf-lib``.
    2.  Review ``9XX-gui-pdf-editor-template`` for component structure and adapt as needed.
    3.  Set up a dedicated module/directory within ``gui/src/renderer/`` for PDF editor components (e.g., ``gui/src/renderer/components/PdfEditor/``).
    4.  Basic POC: Load and display a PDF using ``react-pdf``.
    5.  Basic POC: Use ``pdf-lib`` to add simple text to a PDF and save it (client-side initially).
*   **Deliverables**:
    *   Working PDF display component.
    *   POC demonstrating ``pdf-lib`` text addition.

Phase 2: Basic PDF Viewer Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Implement a robust PDF viewer within the GUI.
*   **Tasks**:
    1.  Develop the main ``PdfEditorViewer`` React component.
    2.  Implement PDF loading from a file path (via Electron IPC).
    3.  Implement multi-page navigation (thumbnails, page number input, next/previous).
    4.  Implement zoom functionality (zoom in, zoom out, fit to page, fit to width).
    5.  Ensure proper rendering of various PDF content types (text, vector graphics, images).
*   **Deliverables**:
    *   A functional PDF viewer integrated into the application.

Phase 3: Core Editing Features (Client-Side using ``pdf-lib``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Implement fundamental PDF annotation and editing tools. All modifications will initially be handled client-side.
*   **Key UI Element**: An ``AnnotationLayer`` component (SVG or Canvas based) overlaying each rendered PDF page to handle drawing and interaction for new elements.

*   **Sub-Phase 3.1: Text Annotation**
    *   User selects "Add Text" tool.
    *   User clicks on the PDF to place a text box.
    *   User types text into the box.
    *   Basic styling options (font, size, color - MVP).
    *   Text object is added to an internal annotations list managed by React state.

*   **Sub-Phase 3.2: Shape Drawing (Rectangle, Circle)**
    *   User selects "Draw Rectangle" or "Draw Circle" tool.
    *   User clicks and drags to draw the shape.
    *   Basic styling (stroke color, fill color - MVP).
    *   Shape object added to annotations list.

*   **Sub-Phase 3.3: Freehand Drawing (Pencil/Pen Tool)**
    *   User selects "Pencil" tool.
    *   User draws freehand on the PDF.
    *   Basic styling (stroke color, stroke width - MVP).
    *   Path object added to annotations list.

*   **Sub-Phase 3.4: Image Insertion (Simple)**
    *   User selects "Add Image" tool.
    *   User selects an image file (PNG, JPG) via file dialog (Electron IPC).
    *   User clicks to place the image (basic resizing/positioning - MVP).
    *   Image data (and its transformation) added to annotations list.

*   **Deliverables**:
    *   Functional text, shape, freehand drawing, and simple image annotation tools.
    *   Annotations are visually represented on the ``AnnotationLayer``.

Phase 4: Saving & Loading Modified PDFs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Allow users to save their changes and potentially load PDFs with existing compatible annotations (if feasible for MVP).
*   **Tasks**:
    1.  **Saving**:
        *   Implement a "Save" function.
        *   Use ``pdf-lib`` to take the original PDF bytes and apply all annotations from the state list onto the corresponding pages (e.g., ``page.drawText()``, ``page.drawImage()``, ``page.drawSquare()`` etc.).
        *   Generate new PDF bytes (``Uint8Array``).
        *   Use Electron IPC to trigger a "Save File" dialog and write the bytes to the chosen location.
    2.  **Loading Annotations (Post-MVP / Stretch Goal for initial phase)**:
        *   Research methods to store annotation data, possibly as metadata within the PDF or a sidecar file if direct embedding proves too complex for all types with ``pdf-lib``.
*   **Deliverables**:
    *   Users can save PDFs with their client-side annotations embedded.

Phase 5: Backend Integration (Python - For Complex/Future Tasks)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Identify and implement any PDF operations that are too complex or inefficient for client-side ``pdf-lib`` and are better suited for Python backend libraries.
*   **Context**: Refer to ``8XX-pdf-editing-workflow`` for library suggestions (e.g., ``pypdf``, ``borb`` for AcroForms, ``pdf2docx`` if form flattening or complex manipulations are needed).
*   **Potential Tasks (Examples, to be evaluated based on need)**:
    *   Filling existing AcroForm fields.
    *   Flattening annotations or form fields.
    *   More complex image processing before insertion.
    *   OCR on a specific region to make text editable.
*   **Implementation**:
    *   Define Python functions in a new module (e.g., ``src/aichemist_transmutation_codex/converters/pdf_editing_tools.py``).
    *   Expose these functions via ``electron_bridge.py`` using the established JSON messaging protocol.
    *   Call from Electron main process and expose to renderer via ``preload.ts``.
*   **Deliverables**:
    *   Identified backend tasks (if any for MVP).
    *   Implemented Python functions and IPC bridge for these tasks.

Phase 6: UI/UX Refinement & Toolbar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Create an intuitive user interface for the editor.
*   **Tasks**:
    1.  Design and implement a ``Toolbar`` React component as per ``9XX-gui-pdf-editor-template``.
        *   Buttons for selecting tools (Text, Shape, Pen, Image).
        *   Controls for selected tool properties (color, size, font).
        *   Zoom controls.
        *   Save button.
    2.  Implement selection and modification of existing annotations (MVP: select, delete. Moving/resizing can be Post-MVP).
    3.  Provide visual feedback for active tools and selections.
    4.  Ensure responsive design within the Electron window.
    5.  Styling using TailwindCSS and Shadcn/UI.
*   **Deliverables**:
    *   A user-friendly toolbar and intuitive interaction for editing tools.

Phase 7: Testing
~~~~~~~~~~~~~~~~
*   **Objective**: Ensure the reliability and correctness of the PDF editor.
*   **Tasks**:
    1.  **Unit Tests (Frontend - Vitest/Jest)**:
        *   Test individual React components (Toolbar, AnnotationLayer, PdfEditorViewer).
        *   Test ``pdf-lib`` integration logic (e.g., annotation application).
    2.  **Integration Tests (Frontend/Electron)**:
        *   Test IPC communication for file loading/saving.
    3.  **E2E Tests (Optional - using Playwright or similar for Electron)**:
        *   Simulate user workflows (load PDF, add annotations, save PDF).
    4.  **Manual Testing**:
        *   Test with a variety of PDF files (different versions, sizes, content complexities).
        *   Verify output in multiple PDF viewers (Adobe Acrobat, browser viewers).
    5.  **Backend Unit Tests (Python - Pytest)**:
        *   If any backend Python functions are implemented (Phase 5), they need thorough unit tests.
*   **Deliverables**:
    *   A suite of automated tests.
    *   Manual test plan and results.

Phase 8: Documentation
~~~~~~~~~~~~~~~~~~~~~~
*   **Objective**: Document the new feature for users and developers.
*   **Tasks**:
    1.  **User Documentation**:
        *   Update GUI help sections/tooltips to explain how to use the PDF editor features.
    2.  **Developer Documentation**:
        *   Add JSDoc/TSDoc comments to new React components and TypeScript functions.
        *   If Python backend code is added, write Google-style docstrings.
        *   Update relevant architecture documents or create new ones if the editor introduces significant new patterns not covered by ``9XX-gui-pdf-editor-template``.
        *   Update this plan (``pdf_editor_development_plan.rst``) with any deviations or more detailed decisions made during development.
*   **Deliverables**:
    *   Updated user and developer documentation.

Key Considerations
------------------

*   **Performance**: PDF rendering and manipulation, especially with large files or many annotations, must be performant to ensure a smooth user experience. Optimize ``pdf-lib`` usage and React component rendering.
*   **Memory Management**: Be mindful of memory usage when handling large PDFs or many image annotations client-side.
*   **Error Handling**: Implement robust error handling for file operations, PDF parsing issues, and annotation tool errors. Provide clear feedback to the user.
*   **Security**: Follow Electron security best practices, especially for IPC and file system access.
*   **Undo/Redo**: (Post-MVP) Implementing a reliable undo/redo stack for annotations can be complex but highly valuable.
*   **Cross-PDF Viewer Compatibility**: Aim for annotations to be visible and correctly rendered in common PDF viewers.

Future Enhancements (Post-MVP)
------------------------------

*   Advanced text editing (rich text, block editing).
*   More shape types (arrows, lines).
*   Annotation properties editor (more detailed control over styling).
*   Page manipulation (reorder, delete, rotate pages).
*   Form filling (AcroForms) - may require backend Python (e.g., ``pypdf``).
*   Redaction.
*   Measurement tools.
*   Collaboration features (if applicable to the broader project).

This plan will be updated as development progresses and more detailed requirements or technical challenges emerge.