# Feature Specification: Frontend Knowledge Base & Interactive Chat UI

**Feature Branch**: `003-frontend-rag-ui`

**Created**: 2026-11-13

**Status**: Draft

**Input**: User description: "Interface web do Atlas AI com Vue 3, TypeScript, Pinia, Tailwind CSS: gerenciamento de bases de conhecimento, upload de documentos e chatbot com visualização de fontes"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Knowledge Bases Management View (Priority: P1) 🎯 MVP

As a user or researcher, I want to access a clean, modern web interface that lists all my knowledge bases, allows creating new ones with title and description, and provides quick navigation to manage documents or open chat sessions, so that I can organize my knowledge domains intuitively.

**Why this priority**: The Knowledge Bases dashboard is the main entry point to the entire platform; without it, users cannot select a domain or access subsequent features.

**Independent Test**: Can be fully tested by launching the web application, viewing the collection of knowledge bases, creating a new knowledge base via a creation modal/form, and verifying that the new card appears immediately with accurate metadata and 0 documents.

**Acceptance Scenarios**:
1. **Given** the user lands on the application home page, **When** knowledge bases exist, **Then** the interface displays cards for each base showing its name, description, total document count badge, and creation date.
2. **Given** the user is on the dashboard, **When** they click "Create Knowledge Base" and fill out the name and optional description, **Then** the system creates the base, closes the modal, and renders the new card without requiring a full page reload.
3. **Given** an attempt to submit a blank name or duplicate name, **When** the creation button is clicked, **Then** the interface displays an inline validation message and keeps the form open.

---

### User Story 2 - Document Upload and Ingestion Monitoring (Priority: P1)

As a user, I want to upload files (PDF, TXT, Markdown) into a selected knowledge base using drag-and-drop or a file picker, and monitor the ingestion processing state in real-time, so that I know when my documents are ready for semantic querying.

**Why this priority**: Ingesting content is necessary to populate the vector database with reference chunks. Visual feedback on upload and processing status prevents user confusion during background embedding operations.

**Independent Test**: Can be fully tested by selecting a knowledge base, dragging a Markdown or PDF document into the upload dropzone, observing the upload progress indicator, and verifying that the document row updates its badge to "Completed" with the count of generated chunks.

**Acceptance Scenarios**:
1. **Given** a knowledge base detail view, **When** the user drags a supported file (PDF, TXT, Markdown up to 10 MB) into the dropzone or clicks the file selector, **Then** the UI uploads the file, displays a loading indicator, and adds a new document row with status "Processing".
2. **Given** a document that finishes parsing and embedding, **When** processing succeeds, **Then** the status badge transitions to "Completed" (green) and displays the total number of generated chunks.
3. **Given** an invalid file (unsupported format or size > 10 MB), **When** the user attempts an upload, **Then** the interface immediately halts the upload, displays a red alert message explaining the restriction, and retains existing document items.
4. **Given** an uploaded document, **When** the user clicks the delete icon and confirms, **Then** the document is removed from the list and storage.

---

### User Story 3 - Interactive Chat Interface with Grounded Citations (Priority: P1)

As a user, I want to interact with a conversational chatbot scoped to the selected knowledge base, sending natural language questions and reading grounded answers accompanied by expandable source citation pills, so that I can audit the factual basis of every claim made by the assistant.

**Why this priority**: Chatting with documents and inspecting sources is the core value proposition of the Atlas AI RAG experience.

**Independent Test**: Can be fully tested by opening the chat view of a populated knowledge base, asking a question about the uploaded document, and verifying that the assistant bubble renders the synthesized text and presents citation pills that reveal the excerpt, file name, and similarity score when clicked.

**Acceptance Scenarios**:
1. **Given** an active chat view, **When** the user types a question and presses Enter or clicks Send, **Then** the user message is immediately rendered in the dialogue stream, an animated "Assistant is thinking..." indicator appears, and the input field clears.
2. **Given** a synthesized response received from the backend, **When** the assistant message renders, **Then** it presents the formatted markdown text and a list of citation pills (e.g., "[1] manual_arquitetura.pdf (89% relevância)").
3. **Given** citation pills under an assistant message, **When** the user clicks a citation pill, **Then** an expandable drawer or popover displays the exact text snippet retrieved from the document and its chunk index.
4. **Given** a knowledge base with no documents or an unanswerable question, **When** the assistant responds, **Then** the message clearly explains that no relevant information was found, with zero ungrounded claims.

---

### User Story 4 - Multi-Session Chat Navigation & Deletion (Priority: P2)

As a user, I want a sidebar listing my conversation sessions within a knowledge base, allowing me to start a new chat, switch between previous discussions, or delete outdated sessions, so that my research workflows remain organized.

**Why this priority**: Separating conversations by topic or query objective prevents context pollution and empowers users to manage multiple inquiry threads.

**Independent Test**: Can be fully tested by creating a second chat session, switching between session 1 and session 2, confirming that each preserves its own message history, and deleting session 1 to ensure it disappears from the sidebar.

**Acceptance Scenarios**:
1. **Given** the chat view, **When** the user views the left sidebar, **Then** it lists all conversation sessions sorted by most recent activity, displaying the title and relative timestamp.
2. **Given** multiple sessions, **When** the user clicks another session in the sidebar, **Then** the active dialogue window loads that session's chronological messages immediately.
3. **Given** a session in the sidebar, **When** the user clicks "Delete Session" and confirms the prompt, **Then** the session is removed from the sidebar, and the view redirects to the most recent session or an empty chat state.

---

## Edge Cases

- **Network Offline or Backend Unreachable**: When the frontend cannot communicate with the API, an unobtrusive banner or toast notification must appear: *"Não foi possível conectar ao servidor. Verifique se o backend está em execução."*
- **Empty Knowledge Base State**: If a user opens the chat on a knowledge base with 0 documents, the chat view must display a helpful empty state card: *"Esta base de conhecimento ainda não possui documentos. Envie arquivos para começar a conversar."* with a direct button to the Documents tab.
- **Large Text Citations**: If a chunk has 500 characters, the preview pill must truncate neatly with ellipsis, expanding fully only upon user interaction.
- **Rapid Successive Submissions**: The send button must be disabled while a request is in flight to prevent duplicate submissions.
- **Mobile Screen Widths**: On mobile viewports (< 768px), the session sidebar must collapse into a hamburger drawer to preserve chat readability.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The frontend MUST be developed as an independent SPA communicating exclusively via HTTP REST with `/api/v1`.
- **FR-002**: The interface MUST provide a responsive dashboard displaying Knowledge Base cards with title, description, document counts, and action shortcuts.
- **FR-003**: The interface MUST provide a drag-and-drop document upload zone supporting `.pdf`, `.txt`, and `.md` files up to 10 MB.
- **FR-004**: The interface MUST display real-time status badges for uploaded documents (`pending`, `processing`, `completed`, `failed`) with error tooltips if failed.
- **FR-005**: The interface MUST support deleting documents and deleting knowledge bases with explicit user confirmation modals.
- **FR-006**: The interface MUST feature an interactive chat view with distinct visual styling for `user` messages and `assistant` messages.
- **FR-007**: The interface MUST render markdown formatting (headers, lists, bold text, code blocks) in assistant messages.
- **FR-008**: The interface MUST render interactive source citations for each assistant message, displaying the source filename, chunk position, similarity percentage, and expandable text excerpt.
- **FR-009**: The interface MUST include a conversation session sidebar allowing users to create new sessions, switch between sessions, and delete existing sessions.
- **FR-010**: The interface MUST implement global state management for knowledge bases, active documents, and chat sessions to avoid redundant network round-trips.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Initial page load and dashboard rendering must complete in under 1.2 seconds on standard broadband connections.
- **SC-002**: 100% of button clicks and interactions must provide immediate visual feedback (< 100 ms) via loading states or active spinners.
- **SC-003**: 100% of assistant messages with source citations must allow inspecting the exact text snippet with a single click.
- **SC-004**: The application layout must be responsive, adapting without horizontal scrollbars across desktop (1440px), laptop (1024px), tablet (768px), and mobile (375px) viewports.

---

## Assumptions

- Users access the application using modern evergreen web browsers (Chrome, Firefox, Safari, Edge) with JavaScript enabled.
- The backend API is hosted at the configurable base URL specified by `VITE_API_BASE_URL` (default: `http://localhost:8000/api/v1`).
- Dark mode support can be added as a subsequent visual enhancement; the baseline deliverable delivers a clean, accessible, modern light theme with high contrast.
