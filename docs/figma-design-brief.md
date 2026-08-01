# Doitall Figma Design Brief

## Source context and assumptions

This brief is the single design reference for generating Doitall's web UI in Figma. It is based on the existing frontend planning, product requirements, user-flow, information architecture, visual design, and component documentation, plus a repository review of the current FastAPI backend, API models, commands, provider registry, knowledge ingestion, memory, and skills modules.

### Current product capabilities to design for

- Chat requests and streamed chat responses using `/v1/chat` and `/v1/chat/stream`.
- Persistent session list, session detail, and session deletion.
- Provider listing with default and availability status.
- Slash command discovery through `/v1/commands`.
- Text-based knowledge ingestion through `/v1/knowledge/ingest`.
- Health and readiness status through `/v1/health/live`, `/v1/health/ready`, and `/v1/health`.
- Optional API-key authentication for protected endpoints.
- Backend-supported memory, RAG, and tool/skill execution exist conceptually, but not all management or observability APIs are exposed to the frontend.

### Explicit assumptions

- Design should include Memory and Tools & Skills as capability-gated or roadmap-aware product areas, not as fully editable/administerable MVP screens.
- Knowledge upload, document list/detail/delete, memory search/edit/delete, account login, user profiles, tool execution history, and cancellation are future capabilities unless backend APIs are added.
- Session names are not currently supported; session rows should use smart fallbacks such as recent message snippets, timestamps, message counts, and visible session IDs.
- Figma should create dark mode first and provide light mode-compatible tokens, but final implementation technology is not prescribed by this brief.

---

## 1. Product Overview

### What the application is

Doitall is a browser-based AI agent workspace for interacting with a FastAPI-powered AI assistant platform. It combines conversational AI, persistent chat sessions, selectable LLM providers, text knowledge ingestion for retrieval-augmented generation, slash-command discovery, health/status visibility, and developer-oriented connection settings.

### Primary problem it solves

Doitall turns a technical AI agent backend into a transparent, usable web product. It helps builders and operators test, debug, and trust agent interactions without relying only on CLI commands, raw API calls, or backend logs.

### Target users

- **AI application developers:** Test chat, providers, sessions, commands, tool behavior, memory/RAG effects, and streaming.
- **Product teams:** Validate agent workflows and demo reliable AI experiences.
- **Operators/admins:** Monitor backend readiness, provider availability, degraded services, and connection issues.
- **QA/support teams:** Reproduce conversations using session IDs, timestamps, request state, and error messages.
- **Knowledge workers/end users:** Chat with the assistant, resume sessions, and ingest text knowledge without needing API knowledge.

### Product goals

- Make the first successful streamed chat fast and obvious.
- Preserve and expose session context in a way that builds user trust.
- Surface provider availability, health, auth, and degraded backend states clearly.
- Provide a polished foundation for future tools, skills, memory, knowledge management, and admin surfaces.
- Support keyboard-first, accessible, responsive workflows for technical and non-technical users.

---

## 2. Design Goals

The experience should feel:

- **Professional:** Trustworthy enough for developers, operators, and internal product demos.
- **Modern and premium:** Refined surfaces, restrained depth, excellent typography, and precise state design.
- **Fast:** Low-friction entry, immediate feedback, optimistic chat updates, and visible streaming progress.
- **Minimal but transparent:** Avoid unnecessary chrome while clearly showing health, provider, auth, and error states.
- **AI-first:** Treat streaming, safe thinking labels, command discovery, and tool/knowledge context as core product moments.
- **Developer-friendly:** Make session IDs, provider status, diagnostics, commands, and API connection state easy to inspect.
- **Accessible:** Keyboard navigable, screen-reader considerate, high contrast, clear focus states, and responsive.
- **Extensible:** Design patterns should scale to future memory, tool, run, knowledge, account, and admin capabilities.

---

## 3. Visual Style

### Design philosophy

Use the Doitall visual language of **Quiet Intelligence**:

- **Graphite precision:** Dark neutral surfaces, crisp borders, and measured layout density.
- **Aurora intelligence:** Blue-violet-cyan accents used sparingly for AI activity, primary actions, focus, and streaming.
- **Layered glass depth:** Subtle translucent panels and soft shadows that create hierarchy without visual noise.
- **Human-readable density:** Spacious chat reading areas with compact operational panels.
- **State transparency:** Visual hierarchy should immediately communicate ready, degraded, unavailable, streaming, blocked, retryable, or complete.

### Typography direction

- Use a modern neutral sans-serif for UI and message content.
- Use a high-legibility monospaced typeface for IDs, commands, code, JSON, provider names when technical, and diagnostics.
- Assistant answers should feel editorial and readable with generous line height.
- Operational metadata should be smaller, subdued, and precise.
- Avoid playful type, decorative fonts, heavy all-caps usage, and dense paragraph blocks in operational UI.

### Color direction

Design dark mode first:

- **Base:** Graphite, slate, charcoal, and near-black surfaces.
- **Primary accent:** Aurora violet/indigo for primary actions, selected navigation, focus rings, and important AI moments.
- **Secondary accent:** Cyan for streaming/live status, connection, and active processing.
- **Status:** Green for ready/success, amber for degraded/warning, red for failure/destructive, blue for informational.
- **Light mode compatibility:** Preserve the same semantic relationships using pale neutral backgrounds, strong text contrast, and restrained accents.

Avoid copying any specific AI/SaaS product palette. Accents should be luminous but controlled.

### Spacing principles

- Use an 8 px base spacing rhythm with 4 px micro-adjustments for dense controls.
- Chat content should breathe: large vertical rhythm, comfortable message widths, and clear separation between turns.
- Operational cards can be denser but should maintain clear grouping and scan paths.
- Sidebars should be compact but not cramped; session rows need enough room for timestamp, count, and state.

### Corner radius

- Use soft modern rounding rather than fully pill-shaped everything.
- Suggested visual range:
  - Small controls: 8 px.
  - Inputs/buttons/cards: 10–14 px.
  - Large panels/modals/composer: 16–24 px.
  - Badges/chips: pill only when semantically chip-like.

### Elevation

- Prefer borders, tonal layering, and subtle ambient shadows over heavy drop shadows.
- Use elevation to distinguish shell, floating composer, command palette, dialogs, dropdowns, and context panels.
- In dark mode, elevation can rely on surface brightness differences plus faint aurora/cyan glows for active AI states.

### Icon style

- Use simple line icons with consistent stroke weight.
- Icons should clarify state/action, not decorate every label.
- Use product-specific metaphors sparingly: sparkles for AI, terminal for commands/development, database/book for knowledge, activity/pulse for status.
- All icon-only actions need visible tooltips and accessible labels.

### Animation style

- Subtle, purposeful, fast.
- Prefer 120–220 ms transitions for hover, focus, panel changes, and menu open/close.
- Streaming and thinking indicators may have a gentle pulse or shimmer but must not distract from reading.
- Avoid bouncy, playful, or overly elaborate motion.

---

## 4. Navigation

### Sidebar

Use a persistent global sidebar on desktop with:

- Product mark/name: **Doitall**.
- Primary destinations:
  - Chat
  - Knowledge
  - Dashboard / Status
  - Memory
  - Tools & Skills
  - Settings
- Global status summary:
  - Backend live/unreachable
  - Readiness ready/degraded/error
  - Provider availability count
- Utility actions:
  - Command palette
  - Global/local search entry point
  - Help/API docs link when appropriate

### Chat context sidebar

Chat should add a secondary context sidebar containing:

- New chat button.
- Local session filter/search input.
- Recent session list ordered by last activity.
- Session row metadata: fallback title/snippet, last activity, message count, active state.
- Row actions: open and delete with confirmation.
- Footer with refresh and current session ID copy action when applicable.

### Top navigation

Use a page-specific top bar with:

- Breadcrumb/current page title.
- Page-level primary action.
- Provider selector on Chat and where relevant.
- Readiness badge.
- Auth/API connection status.
- Search and command palette buttons.
- Optional last-refreshed timestamp on status pages.

### Search

- MVP search is primarily local filtering for sessions and command palette items.
- Do not imply global backend search for knowledge/memory/sessions until APIs exist.
- Global search entry can open a capability-aware palette that clearly labels supported and future areas.

### Global actions

- New chat.
- Open command palette.
- Refresh status/providers/sessions depending on context.
- Connect/configure API.
- Toggle theme once appearance settings exist.

### Context panels

Use context panels to show secondary, task-adjacent details without interrupting the primary flow:

- Chat session details: session ID, created/last accessed, message count, provider selection, safe progress state.
- Knowledge ingestion help/result details.
- Status diagnostics: API base URL, docs links, service details.
- Settings validation result.

### Breadcrumbs

- Use concise breadcrumbs in the top nav title area.
- Example: `Chat / Session abc…123`, `Knowledge / Ingest text`, `Settings / API connection`.
- Breadcrumbs should support URL-addressable state and QA/support reproducibility.

### User menu

MVP should not imply full accounts. Use a connection/user menu that includes:

- API connection state.
- API base URL.
- API key present/missing/invalid state.
- Clear key.
- Theme/appearance.
- Future placeholder for profile/account only if visually capability-gated.

---

## 5. Screen List

### 5.1 App entry / connection setup

- **Purpose:** Help users connect to a reachable Doitall API when the backend is unavailable or protected.
- **Primary users:** Developers, operators, local users, API-key users.
- **Main actions:** Edit API base URL, enter API key, retry connection, clear saved key, open diagnostics.
- **Required components:** Setup card, API connection form, status badge, inline validation, backend unavailable state, retry button.
- **Information hierarchy:** Clear problem statement first; current API URL and auth state second; actions third; troubleshooting hints last.

### 5.2 Chat — empty/new session

- **Purpose:** Provide the fastest path to the first chat.
- **Primary users:** All users.
- **Main actions:** Type message, choose provider, select example prompt, open commands, configure API if blocked.
- **Required components:** Empty state hero, prompt suggestion cards, provider selector, chat composer, session sidebar, degraded/no-provider banner.
- **Information hierarchy:** Composer and value proposition first; setup blockers next; examples and tips below.

### 5.3 Chat — active session

- **Purpose:** Conduct and resume persistent AI conversations.
- **Primary users:** Developers, product teams, end users, QA/support.
- **Main actions:** Send message, view streaming answer, switch provider for next turn, retry after failure, copy content/code/session ID, delete/open sessions.
- **Required components:** Message timeline, chat bubbles, assistant message, user message, streaming indicator, safe thinking indicator, composer, provider selector, session list, session details panel, error message card.
- **Information hierarchy:** Conversation timeline is primary; composer is anchored and prominent; provider/status metadata is visible but secondary.

### 5.4 Chat — loading, streaming, and error states

- **Purpose:** Keep users oriented during async agent work.
- **Primary users:** All users.
- **Main actions:** Wait, retry, inspect public progress, recover from stream errors.
- **Required components:** Skeleton messages, token streaming state, thinking/progress label, inline error card, retry action, degraded banner.
- **Information hierarchy:** Current state label near the pending assistant message; retry/remediation near the failed message; global health remains visible.

### 5.5 Session not found

- **Purpose:** Recover from deleted, stale, or invalid session URLs.
- **Primary users:** QA/support, returning users, developers.
- **Main actions:** Start new chat, return to recent sessions, refresh sessions.
- **Required components:** Not-found state, session ID display, new chat button, session list.
- **Information hierarchy:** Explain the missing session; show safe next actions; keep technical ID copyable.

### 5.6 Knowledge — text ingestion

- **Purpose:** Add text documents to the knowledge base for future retrieval.
- **Primary users:** Developers, product teams, knowledge workers, operators.
- **Main actions:** Enter title, paste content, add optional metadata, submit ingestion, copy document ID.
- **Required components:** Knowledge ingest form, title input, large content text area, metadata editor, submit button, validation messages, ingestion result card.
- **Information hierarchy:** Form first; constraints/help text nearby; result confirmation beside or below form; future unavailable document management separated clearly.

### 5.7 Knowledge — success/error result

- **Purpose:** Confirm ingestion outcome and explain what happens next.
- **Primary users:** Developers, knowledge workers, QA.
- **Main actions:** Copy document ID, ingest another document, go to Chat, review validation errors.
- **Required components:** Ingestion result card, key-value list, status badge, error alert, empty/future document list placeholder.
- **Information hierarchy:** Status and document ID first; chunk count second; next steps third.

### 5.8 Dashboard / Status

- **Purpose:** Show whether the system is reachable, ready, and provider-capable.
- **Primary users:** Operators, developers, QA/support.
- **Main actions:** Refresh status, inspect service details, inspect providers, open settings/API docs.
- **Required components:** Status overview cards, health status cards, provider status cards, diagnostics panel, refresh button, timestamp.
- **Information hierarchy:** Overall status at top; dependency details next; provider cards; diagnostics links and request/session metadata last.

### 5.9 Providers status panel/page

- **Purpose:** Explain available configured providers and default provider state.
- **Primary users:** Developers, operators, chat users.
- **Main actions:** Select provider for chat, refresh provider checks, navigate to settings if none available.
- **Required components:** Provider status cards/table, default badge, availability indicator, warning state for slow/failed checks.
- **Information hierarchy:** Available/default providers first; unavailable providers and remediation second; caveat about capabilities third.

### 5.10 Commands palette

- **Purpose:** Make slash commands discoverable and keyboard-first.
- **Primary users:** Developers, power users, designers validating command UX.
- **Main actions:** Open palette, search commands, filter by category, insert command into composer, close without action.
- **Required components:** Command palette overlay, search input, command rows/cards, category labels, keyboard shortcut hints, empty result state.
- **Information hierarchy:** Search field first; matching commands grouped by category; selected command description and arguments visible.

### 5.11 Tools & Skills

- **Purpose:** Orient users to current command/tool/skill capabilities without overpromising unsupported admin controls.
- **Primary users:** Developers, operators, product teams.
- **Main actions:** Browse commands, understand built-in skills conceptually, return to chat, view roadmap/capability-gated controls.
- **Required components:** Capability-gated landing page, command cards, tool/skill explanation cards, future execution history placeholder.
- **Information hierarchy:** Current command discovery first; tool/skill limits second; future controls visually disabled or marked unavailable.

### 5.12 Memory

- **Purpose:** Explain memory as a backend capability and future management surface.
- **Primary users:** Developers, operators, designers, future admins.
- **Main actions:** Understand memory availability, view capability-gated roadmap, return to chat/settings.
- **Required components:** Capability-gated empty state, memory concept cards, future memory card/table examples clearly marked as not currently actionable.
- **Information hierarchy:** Current limitation first; why memory matters second; future management concepts third.

### 5.13 Settings — API connection

- **Purpose:** Configure frontend connection to the backend.
- **Primary users:** Developers, operators, local/self-hosted users.
- **Main actions:** Edit API base URL, enter/update/clear API key, test connection, view auth state.
- **Required components:** Settings section, API connection form, key input with secure display behavior, test connection button, success/error alerts.
- **Information hierarchy:** Current connection state; editable fields; validation/test result; security caveats.

### 5.14 Settings — provider preference and appearance

- **Purpose:** Persist user-friendly local preferences.
- **Primary users:** All users.
- **Main actions:** Choose default local provider preference, choose theme, review accessibility/density options.
- **Required components:** Select inputs, segmented controls, status badges, settings cards.
- **Information hierarchy:** Provider preference; appearance; future account/workspace settings marked as unavailable.

### 5.15 Unauthorized / rate-limited / degraded-state screens

- **Purpose:** Provide clear recovery for common failure modes.
- **Primary users:** All users, especially local/API-key users.
- **Main actions:** Enter API key, retry, change base URL, wait/retry after rate limit, open status.
- **Required components:** Error state, alert/banner, API key dialog, retry button, troubleshooting links.
- **Information hierarchy:** What happened; why it likely happened; what to do next; technical details collapsed.

---

## 6. User Journeys

### Login / API connection setup

1. User opens app.
2. App checks public health/provider status.
3. If protected requests fail, user sees API connection setup.
4. User enters API base URL and/or development API key.
5. App validates connection and returns to prior destination.
6. User can clear the key later from Settings.

### Dashboard/status journey

1. User opens Dashboard or sees a degraded banner.
2. User reviews overall live/ready state.
3. User inspects dependency/service cards.
4. User reviews provider availability.
5. User refreshes or navigates to Settings if remediation is needed.

### Chat journey

1. User starts from empty Chat or selects a past session.
2. User confirms or changes provider.
3. User sends a non-empty message.
4. UI appends the user message immediately.
5. Backend returns/streams session information and assistant content.
6. UI shows safe public thinking/progress labels and streaming text.
7. On completion, session history refreshes and the conversation remains resumable.

### Tool execution visibility journey

- Current UI should only show safe persisted tool-result messages when present in history.
- Do not design raw internal tool traces as if supported by current stream events.
- Future designs can include a collapsible tool timeline with tool call, tool result, status, duration, and safe output once APIs exist.

### Skill execution journey

- Current user-facing skill discovery is primarily through commands and conceptual Tools & Skills pages.
- Built-in skills such as calculator, filesystem, and time should not be exposed as fully configurable admin entities unless backend endpoints are added.
- Future skill execution/admin designs must distinguish safe user-visible output from privileged internal filesystem or execution details.

### Memory management journey

- Current backend memory exists, but frontend management APIs are not available.
- MVP should show memory as a capability-gated explanatory surface.
- Future journey: list/search memories, inspect provenance, edit/delete, and manage namespaces/permissions.

### Settings journey

1. User opens Settings.
2. User reviews API connection and auth state.
3. User tests connection.
4. User updates provider preference or appearance.
5. User sees success/error feedback and can return to Chat.

### File handling journey

- Current backend supports text knowledge ingestion, not general file upload through the web UI.
- Do not include an active file upload screen in MVP.
- Future file handling can be represented as disabled/capability-gated: drag-and-drop upload, parsing status, ingestion job progress, and document list.

---

## 7. Layout Principles

### Grid system

- Use a 12-column desktop grid for full pages.
- Use nested 4/6/8-column grids inside cards and panels where helpful.
- Maintain an 8 px spacing system.
- Use consistent gutters: larger on desktop, reduced on tablet/mobile.

### Content width

- Chat message column should be readable, not full-bleed. Target roughly 720–900 px for message text on desktop.
- Operational pages can use wider card grids up to approximately 1200–1440 px.
- Forms should avoid excessive width: ingestion content area can be wide; metadata and settings fields should remain scan-friendly.

### Desktop

- Persistent global sidebar.
- Optional context sidebar for Chat and page-specific navigation.
- Top nav always visible.
- Chat composer anchored near bottom of content area.
- Context panels may sit on the right side when space allows.

### Tablet

- Global sidebar can collapse to icons or become a drawer.
- Chat session list should be a drawer or collapsible pane.
- Main content remains primary; composer stays reachable.
- Cards stack into one or two columns depending on width.

### Mobile

- Prioritize core chat actions.
- Use bottom navigation or drawer for global nav.
- Session list, provider selector, command palette, and settings should open as sheets/drawers.
- Composer should remain easy to reach with touch-friendly controls.
- Avoid showing dense diagnostics by default; use progressive disclosure.

---

## 8. Components

### Foundations

- **Buttons:** Trigger actions; support primary, secondary, ghost, danger, link, loading, disabled, and full-width mobile states.
- **Icon buttons:** Compact actions for copy, refresh, delete menu, close, search, command palette, theme, and drawer controls; require labels/tooltips.
- **Inputs:** Text input, text area, select, search, API key input, and metadata editor; include labels, helper text, validation, and disabled/loading states.
- **Badges/status indicators:** Show ready, degraded, unavailable, default provider, selected, streaming, authenticated, missing key, capability-gated, and future states.

### Data display

- **Cards:** Flexible containers for status, provider, prompt suggestions, settings, ingestion results, and capability descriptions.
- **Tables/lists:** Provider lists, command lists, future memory/document lists; support empty/loading/error states.
- **Key-value lists:** Session IDs, document IDs, chunk count, health details, API base URL, timestamps.
- **Timestamps:** Relative and absolute where useful; support tooltips for exact values.

### Chat and AI components

- **Chat messages/bubbles:** Distinguish user, assistant, tool-safe, system/error, and streaming states. Assistant content should be more editorial; user content can be compact.
- **Message timeline:** Chronological, scrollable, accessible landmarks, loading restoration state, and anchor behavior for new messages.
- **Chat composer:** Multiline input, send button, provider context, command affordance, disabled state when streaming, validation for empty input, draft preservation.
- **Streaming indicator:** Shows active response generation and token arrival without exposing raw SSE.
- **Thinking indicator:** Safe public progress labels only; never expose hidden reasoning.
- **Code blocks:** Monospaced, readable, copy action, language label if known, horizontal scroll for long lines.
- **Markdown renderer:** Supports common answer formatting while treating content as untrusted.
- **Tool cards/timeline items:** MVP should be safe/read-only for persisted tool messages; future-ready for structured status and results.
- **Memory cards:** Capability-gated/future-ready; show content, provenance, confidence, source, and actions only when supported.

### Navigation and layout components

- **App shell:** Coordinates global sidebar, top nav, content, context sidebars, status banners, and responsive drawers.
- **Global sidebar:** Primary navigation, status summary, utility actions.
- **Context sidebar:** Chat sessions or page-specific secondary nav.
- **Top nav:** Breadcrumb/title, page actions, provider/status/auth controls.
- **Breadcrumbs:** Concise location and session context.
- **Tabs/accordions:** Settings and secondary page organization.
- **Drawers/sheets:** Mobile/tablet navigation, session list, provider picker, command palette details.

### Overlays and feedback

- **Command palette:** Keyboard-first searchable overlay for commands and supported navigation/actions.
- **Dialogs/modals:** Confirmation, API key setup, destructive delete, unsaved changes.
- **Dropdowns/popovers:** Provider selector, user/connection menu, session row actions.
- **Toasts:** Non-blocking success/failure feedback such as copied ID, session deleted, knowledge ingested.
- **Alerts/banners:** Backend unavailable, degraded readiness, no providers, unauthorized, rate limited.
- **Tooltips:** Explain technical controls without replacing visible labels.

### Page states

- **Empty states:** Welcome chat, no sessions, no commands found, no providers, unsupported future surfaces.
- **Error states:** Backend unreachable, stream failure, validation errors, unauthorized, rate limited, provider unavailable, session not found.
- **Loading skeletons:** Sessions, messages, provider cards, health cards, command palette results.
- **Not-found states:** Session not found and future route gaps.

---

## 9. Accessibility

- **Keyboard navigation:** All navigation, command palette, provider selection, session list, dialogs, forms, and chat composer controls must be keyboard accessible.
- **Focus states:** Use visible high-contrast focus rings; do not rely only on shadows or subtle color shifts.
- **Color contrast:** Meet WCAG 2.2 AA for text and interactive controls in dark and light modes. Status must not rely on color alone.
- **Screen readers:** Use semantic landmarks for app shell, navigation, main content, complementary panels, and status regions. Announce stream start, completion, and errors politely without reading every token individually.
- **Touch targets:** Minimum 44 × 44 px for mobile/touch controls; avoid tiny destructive actions.
- **Forms:** Labels always visible or programmatically associated; validation tied to fields; errors written in plain language.
- **Dialogs:** Trap focus, restore focus on close, support Escape, announce titles/descriptions.
- **Motion sensitivity:** Respect reduced-motion preferences; provide non-animated alternatives for streaming/loading states.
- **Responsive accessibility:** Drawers/sheets must manage focus and reading order correctly on mobile.

---

## 10. Motion

### Page transitions

- Use short fades/slides for page content changes, around 120–180 ms.
- Keep shell/sidebar stable to avoid disorientation.
- Prefer preserving chat scroll position and draft state during navigation.

### Loading animations

- Use skeletons for sessions, provider cards, health cards, and message restoration.
- Use subtle shimmer only when helpful; avoid constant high-contrast motion.
- Use determinate progress only when actual progress exists; otherwise use clear indeterminate loading.

### Hover effects

- Slight surface lift, border brightening, or accent tint.
- Keep hover effects quiet and consistent across cards, rows, and buttons.

### Button feedback

- Immediate pressed state.
- Loading state prevents duplicate activation.
- Destructive actions require confirmation and use danger styling only at the final step.

### AI response streaming

- Pending assistant message appears immediately after send.
- Tokens should stream smoothly into the message body.
- A small cyan/aurora pulse can indicate active generation.
- Safe thinking labels can update as compact status text near the assistant message.

### Tool execution feedback

- Current: show safe, generic progress when tool-backed responses may arrive as one final chunk.
- Future: show structured tool status as a collapsible timeline with pending, running, success, warning, and failed states.
- Never animate tool output in a way that implies hidden reasoning is visible.

---

## 11. Responsive Design

### Desktop

- Full global sidebar and top nav.
- Chat may use global sidebar + session context sidebar + central message timeline.
- Right context panel is optional for session diagnostics and can collapse.
- Dashboard/status uses multi-column cards.

### Laptop

- Preserve sidebar but allow compact density.
- Context panels can collapse to a button/drawer.
- Chat message column remains centered and readable.

### Tablet

- Global sidebar collapses to icons or drawer.
- Session list becomes collapsible side drawer.
- Top nav remains with condensed controls.
- Provider selector and command palette use popovers/sheets.

### Mobile

- Chat-first layout.
- Bottom or hamburger navigation.
- Composer fixed near bottom with safe-area spacing.
- Session history, provider selector, command palette, and settings subsections open as full-screen or bottom sheets.
- Operational dashboards stack vertically with summary first.

---

## 12. Design Constraints

- Current backend supports static optional API-key auth, not account login/sign-up. Do not design account-first flows as MVP.
- Browser-stored API keys should be framed as development/self-hosted connection credentials, not production-grade user authentication.
- Session list is currently unpaginated and does not support server-side search, rename, pin, archive, or titles.
- Session detail returns complete message history; design should support long-history loading and future pagination.
- Chat streaming uses POST-based SSE events: `session`, `thinking`, `token`, `done`, and `error`.
- Standard browser EventSource limitations are an implementation concern, but UX should account for stream interruption and retry.
- Tool-related streaming is limited; final responses may arrive as a single chunk when tools are involved.
- No cancellation endpoint currently exists; do not make cancel a required MVP action.
- Provider endpoint exposes name, default, and availability, not model capability matrices.
- Provider health checks may be slow or fail because of external credentials/services.
- Knowledge ingestion is text-only and returns document ID, chunk count, and status. No upload/list/detail/delete/search preview APIs exist yet.
- Memory management APIs are not exposed; Memory UI must be capability-gated or explanatory.
- Tool/skill admin APIs are not exposed; Tools & Skills should focus on command discovery and future-ready patterns.
- Filesystem tools may have sensitive paths/denied-file errors; never expose raw privileged details without safe redaction patterns.
- UI must not expose hidden model reasoning, internal prompts, raw secrets, or unsafe tool internals.

---

## 13. Instructions for Figma AI

Generate a complete, production-ready design system and multi-screen UI for Doitall using this brief as the source of truth.

- Create **multiple layout concepts for each major screen**, especially Chat, Knowledge, Dashboard/Status, Settings, and mobile Chat.
- Design **dark mode first** using the Quiet Intelligence visual language, with compatible light mode tokens.
- Maintain a consistent design language across all screens: typography, spacing, radius, elevation, iconography, color semantics, and motion annotations.
- Use reusable components for navigation, chat, forms, cards, status, dialogs, command palette, empty states, error states, and loading states.
- Prioritize usability and accessibility over visual novelty.
- Show all important states: empty, loading, streaming, degraded, unauthorized, rate-limited, provider unavailable, validation error, backend unavailable, success, and destructive confirmation.
- Clearly distinguish current MVP capabilities from future or capability-gated concepts.
- Do not invent unsupported MVP features such as account login, file upload, knowledge document management, memory editing, tool admin, run cancellation, or global backend search.
- Keep spacing and typography consistent using design tokens.
- Make chat feel premium, readable, and fast, with operational transparency nearby but not overwhelming the conversation.
- Produce developer-friendly designs with visible session IDs, document IDs, provider state, health details, and copy actions where appropriate.
- Ensure every interactive element has clear focus, hover, disabled, loading, and error states.
- Provide responsive variants for desktop, laptop, tablet, and mobile.
- Annotate motion behavior for streaming, loading, page transitions, hover, button feedback, and dialogs.
- Treat all model, tool, markdown, code, knowledge, and metadata output as untrusted content in the design language.
