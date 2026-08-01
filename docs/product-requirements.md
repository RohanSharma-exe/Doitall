# Doitall Frontend Product Requirements Document

## Document status

- **Product:** Doitall web frontend
- **Document type:** Product Requirements Document (PRD)
- **Primary source input:** `docs/frontend-plan.md`
- **Audience:** Product management, product design, frontend engineering, backend engineering, QA, and security reviewers
- **Scope:** Frontend product requirements for a browser-based interface on top of the existing Doitall FastAPI backend
- **Out of scope for this PRD:** Backend implementation details beyond API needs, mobile-native applications, enterprise SSO implementation, and replacement of the existing agent/runtime architecture

## 1. Product vision

Doitall should provide a polished, trustworthy, and developer-friendly web interface for working with AI agents, persistent chat sessions, provider selection, knowledge ingestion, and operational status. The frontend should make the existing backend capabilities approachable without hiding important system behavior such as provider health, streaming state, rate-limit/auth failures, or knowledge-ingestion outcomes.

The first version should deliver a dependable chat workspace that proves the end-to-end value of Doitall: users can start or resume conversations, stream model responses, switch available providers, inspect session history, ingest knowledge, and understand whether the system is healthy. The product should establish a foundation for more advanced agent operations, memory controls, tool observability, and administration in later releases.

### Vision statement

> Enable builders, operators, and teams to interact with Doitall agents through a transparent web workspace that combines conversational AI, persistent context, knowledge augmentation, and operational confidence.

### Product principles

1. **Transparent over magical:** Show safe, user-facing progress states, provider availability, session persistence, and recoverable errors.
2. **Fast path to value:** A user should be able to open the app, send a message, see streaming output, and continue the same session with minimal setup.
3. **Respect operational reality:** Surface degraded health, provider issues, auth requirements, and rate limits rather than failing silently.
4. **Design for future capabilities:** Build extensible UI patterns for tools, skills, memories, knowledge management, runs, and admin controls.
5. **Secure by default:** Avoid exposing production API keys in browsers and provide clear UX for authentication and permissions.
6. **Accessible to all users:** Meet modern accessibility expectations from the first release, especially for streaming and keyboard-driven chat workflows.

## 2. Target audience

### Primary audiences

1. **AI application developers**
   - Need a local or hosted web UI to test Doitall agents, providers, tools, memory, and RAG behavior.
   - Care about API fidelity, streaming visibility, repeatability, and debugging context.

2. **Product teams building AI workflows**
   - Need a usable interface to validate UX concepts, prompt behavior, knowledge ingestion, and session flows.
   - Care about fast iteration, reliable demos, and clear feedback loops.

3. **Internal operators/admins**
   - Need to monitor system health, provider status, and knowledge ingestion outcomes.
   - Care about uptime indicators, degraded-state messaging, and safe administrative controls.

### Secondary audiences

1. **End users of an AI assistant**
   - Need a straightforward chat experience with persistent history and visible progress.
   - Care about low latency, clear errors, and predictable behavior.

2. **QA and support teams**
   - Need to reproduce sessions, verify streaming behavior, and collect user feedback.
   - Care about session IDs, timestamps, errors, and eventual message/run metadata.

3. **Designers**
   - Need a source of truth for surfaces, states, interactions, and constraints.
   - Care about information architecture, content hierarchy, accessibility, empty states, and error states.

## 3. User personas

### Persona A: Developer Dana

- **Role:** Full-stack or AI engineer integrating Doitall into an application.
- **Goals:** Test providers, chat sessions, tool use, knowledge ingestion, and streaming behavior quickly.
- **Pain points:** CLI-only workflows are slow for visual validation; API details are hard to inspect manually; provider failures can be opaque.
- **Needs:** Provider selector, visible session IDs, health status, raw-ish event debugging modes, clear API/auth errors, and generated API types.

### Persona B: Product Manager Priya

- **Role:** Product manager evaluating agent UX and feature readiness.
- **Goals:** Use the product as an end user would, validate workflow completeness, define next iterations.
- **Pain points:** Technical logs are inaccessible; missing APIs or edge cases are discovered late; difficult to compare desired vs. current behavior.
- **Needs:** Stable demo flows, readable states, feature flags/status, roadmap mapping, feedback capture, and clear limitations.

### Persona C: Designer Diego

- **Role:** Product designer creating interaction patterns for chat, streaming, tools, and knowledge workflows.
- **Goals:** Design accessible components that account for loading, errors, long histories, and operational states.
- **Pain points:** AI interfaces often omit edge cases; streaming states can be noisy; tool output can expose sensitive details.
- **Needs:** Message taxonomy, state matrix, safe progress labels, keyboard navigation expectations, and accessibility requirements.

### Persona D: Operator Olivia

- **Role:** Platform/admin operator responsible for uptime and configuration.
- **Goals:** Understand whether Doitall is ready, providers are available, and knowledge ingestion is working.
- **Pain points:** Provider health checks may fail due to credentials or service issues; static browser API keys are risky; local-only rate limits can mislead.
- **Needs:** Health dashboard, provider availability, readiness/liveness status, protected metrics, secure auth pattern, and degraded-state warnings.

### Persona E: Knowledge Worker Kai

- **Role:** End user interacting with Doitall as an AI assistant.
- **Goals:** Ask questions, continue conversations, ingest or reference knowledge, and receive helpful responses.
- **Pain points:** Slow responses without feedback feel broken; lost sessions reduce trust; confusing errors interrupt work.
- **Needs:** Streaming responses, persistent sessions, concise errors, basic knowledge ingestion confirmation, and easy session navigation.

## 4. Product scope

### MVP scope

The MVP should support a complete browser-based workflow for:

1. Starting a chat session.
2. Sending messages through `POST /v1/chat/stream` by default.
3. Falling back to `POST /v1/chat` where streaming is unavailable or disabled.
4. Persisting and resuming sessions using existing session endpoints.
5. Listing and deleting sessions.
6. Selecting an available provider from `/v1/providers`.
7. Listing slash commands from `/v1/commands`.
8. Ingesting text knowledge through `/v1/knowledge/ingest`.
9. Viewing health/readiness status.
10. Handling authentication, rate limiting, provider errors, stream errors, and empty states.

### Non-MVP scope

These items are important but should not block the initial frontend unless explicitly reprioritized:

- Full knowledge document list/detail/delete flows.
- Memory management UI.
- Tool/skill administration UI.
- Model catalog management.
- Multi-user account management.
- Enterprise SSO.
- Mobile-native applications.
- Real-time collaboration.
- Advanced analytics dashboards.

## 5. Core features

### 5.1 Chat workspace

The chat workspace is the primary product surface.

#### Capabilities

- Create a new session implicitly when the user sends the first message.
- Resume an existing session from the sidebar or URL.
- Render user, assistant, tool-result-safe, loading, error, and empty-state messages.
- Stream assistant responses with token-by-token updates when possible.
- Display safe public progress events from the backend `thinking` SSE events.
- Preserve the active `session_id` in route state or URL state.
- Support provider selection per message or per active session.
- Disable the composer while a send/stream is active, with optional future cancellation.
- Provide retry affordance after recoverable failures.
- Show rate-limit/auth/provider errors in plain language.

#### UX states

- Empty chat state with onboarding prompt examples.
- Loading session state.
- Streaming assistant message state.
- Completed assistant response state.
- Stream error state.
- Unknown provider error state.
- Rate-limited state.
- Unauthorized/invalid API key state.
- Backend unavailable/degraded state.

#### Acceptance criteria

- A user can submit a first message and receive a streamed answer.
- The app updates to the returned `session_id` when the backend emits the `session` event.
- Refreshing the page on an existing session route reloads session history.
- Stream tokens append in order without duplicating text.
- A `done` SSE event marks the assistant response complete.
- An `error` SSE event stops streaming and shows a retryable error.
- The UI does not expose hidden model reasoning; only public `thinking` labels are shown.

### 5.2 Session sidebar and history

#### Capabilities

- Fetch sessions from `GET /v1/sessions`.
- Display session rows with title fallback, last activity, and message count.
- Open a session and fetch full history from `GET /v1/sessions/{session_id}`.
- Delete a session using `DELETE /v1/sessions/{session_id}`.
- Highlight the active session.
- Refresh session list after new chat creation, message completion, or deletion.

#### Constraints

- Current backend session list is unpaginated.
- Current backend does not support renaming, pinning, archiving, or searching sessions.
- Current backend detail endpoint returns complete message history.

#### Acceptance criteria

- A user can navigate between at least two sessions without losing active local state.
- Deleting the active session clears the active chat and navigates to a safe empty state.
- Missing sessions return a clear not-found state.

### 5.3 Provider selector

#### Capabilities

- Fetch providers from `GET /v1/providers`.
- Show provider name, default marker, and availability.
- Let users select a provider for a chat request.
- Disable or warn on unavailable providers.
- Preserve the last selected provider locally for convenience.

#### Constraints

- Provider health checks may involve real provider calls and can be slow or fail due to credentials.
- Current provider API does not expose capabilities such as streaming/tool-call support.

#### Acceptance criteria

- Default provider is selected automatically when available.
- If no providers are available, the chat composer shows a blocking configuration message.
- Unknown-provider errors are mapped to provider-selection guidance.

### 5.4 Streaming response experience

#### Capabilities

- Use POST-based SSE against `POST /v1/chat/stream`.
- Parse `session`, `thinking`, `token`, `done`, and `error` events.
- Concatenate token event text into a pending assistant message.
- Render public thinking/progress indicators without exposing chain-of-thought.
- Recover gracefully if a stream terminates unexpectedly.

#### Constraints

- Standard browser `EventSource` does not support POST bodies directly; the frontend should use `fetch` with stream parsing or an equivalent parser.
- When tools are present, the backend may yield the final response as a single chunk rather than true token streaming.
- There is no current cancellation endpoint.

#### Acceptance criteria

- Streaming works in modern Chromium, Firefox, and Safari versions supported by the product.
- The UI does not show raw SSE framing to end users.
- Network interruption results in a visible failed state with retry guidance.

### 5.5 Knowledge ingestion

#### Capabilities

- Provide a form for title, content, and optional metadata.
- Submit to `POST /v1/knowledge/ingest`.
- Show document ID, chunk count, and ingestion status on success.
- Validate empty content before submission.
- Show backend validation errors, including content length and metadata constraints.

#### Constraints

- Current backend supports text ingestion only through JSON body.
- There are no knowledge list, detail, search preview, upload, or delete APIs yet.

#### Acceptance criteria

- A user can ingest a text document and receive clear confirmation.
- The form prevents accidental empty submissions.
- The UI explains that ingested knowledge will be available to future chat retrieval.

### 5.6 Commands palette

#### Capabilities

- Fetch command metadata from `GET /v1/commands`.
- Display commands in a searchable palette.
- Let users insert command text into the composer.
- Hide hidden commands unless an advanced/dev mode requests them.

#### Constraints

- Command execution behavior is not separately exposed; commands primarily assist composer UX.

#### Acceptance criteria

- Keyboard shortcut opens the command palette.
- Selecting a command inserts or applies the command without submitting unexpectedly.

### 5.7 System health and status

#### Capabilities

- Display liveness from `/v1/health/live`.
- Display readiness from `/v1/health/ready`.
- Show degraded services such as Qdrant, database, or provider manager.
- Link to FastAPI docs in development/admin contexts.
- Optionally show metrics availability without exposing protected metrics content.

#### Acceptance criteria

- If readiness returns degraded/503, the UI shows a prominent but non-crashing warning.
- Health status is distinguishable from provider availability.

### 5.8 API key setup for development

#### Capabilities

- Allow local entry of an API key when required by backend configuration.
- Store development API key in browser storage only for local/non-production setups, or rely on a server-side proxy for production.
- Send API key as `Authorization: Bearer <key>` or `X-API-Key` based on implementation choice.
- Provide a way to clear the key.

#### Acceptance criteria

- Unauthorized responses guide the user to configure credentials.
- The frontend does not hard-code production secrets.

## 6. Nice-to-have features

These features improve the product but are not necessary for the initial release.

### Chat enhancements

- Session rename, pin, archive, and search.
- Message edit and regenerate.
- Message-level retry.
- Message feedback with thumbs up/down and comments.
- Copy message, copy code block, and export conversation.
- Markdown rendering with syntax highlighting.
- Attachments once backend supports upload and parsing.
- Prompt templates and prompt history.
- Conversation branching.

### Streaming and agent observability

- Visible `tool_call` and `tool_result` timeline events.
- Run IDs and run history.
- Cancellation button.
- Final token usage, model, latency, and finish reason.
- Debug mode for raw event inspection.

### Knowledge management

- Document list, detail, delete, and re-ingest.
- File upload with drag-and-drop.
- Search preview against knowledge base.
- Metadata filters.
- Ingestion job progress for large documents.

### Memory management

- Memory list and semantic search.
- Edit/delete memory.
- Per-session, per-agent, or per-user memory namespaces.
- Memory provenance and confidence scores.

### Admin and operations

- Public config endpoint integration.
- Provider/model capability matrix.
- Skill/tool registry UI.
- Rate-limit visibility.
- Audit log browser.
- Prometheus dashboard links.

### Experience polish

- Dark/light theme.
- Responsive mobile layout.
- Onboarding checklist.
- Example prompts.
- Keyboard shortcuts.
- Offline/degraded mode messaging.

## 7. Future roadmap

### Phase 0: Product/design alignment

- Confirm MVP scope and target deployment model.
- Define visual design system and information architecture.
- Validate security approach for browser authentication.
- Decide whether frontend is separate from FastAPI or served as static assets/proxy.

### Phase 1: MVP chat frontend

- Implement app shell, session sidebar, provider selector, chat timeline, and composer.
- Integrate `POST /v1/chat/stream`, `GET /v1/sessions`, `GET /v1/sessions/{id}`, `DELETE /v1/sessions/{id}`, and `GET /v1/providers`.
- Add API key setup UX for development.
- Implement core error and empty states.

### Phase 2: Knowledge and status surfaces

- Implement knowledge ingestion form.
- Implement system status page using health endpoints.
- Add command palette using `/v1/commands`.
- Add OpenAPI type generation to frontend build/CI.

### Phase 3: Backend API expansion for frontend completeness

- Add paginated sessions and messages.
- Add session rename/pin/archive/search.
- Add public config/capability endpoint.
- Add tool/skill introspection endpoints.
- Add knowledge document list/search/delete endpoints.
- Add stream metadata and cancellation support.

### Phase 4: Agent transparency and control

- Add safe tool-call/result timeline.
- Add run IDs, run history, cancellation, and resumability.
- Add message feedback and retry.
- Add model/provider capability matrix.

### Phase 5: Administration, memory, and production readiness

- Add memory management UI once namespacing and authorization are defined.
- Add admin dashboards for audit logs, metrics, and configuration warnings.
- Add production auth integration beyond static API keys.
- Add multi-user roles and permissions if product direction requires hosted/team use.

## 8. Functional requirements

### 8.1 Application shell

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-001 | The frontend shall provide a persistent app shell with primary navigation for Chat, Knowledge, Providers/Status, and Settings. | Must |
| FR-002 | The frontend shall show global backend connectivity status. | Must |
| FR-003 | The frontend shall support responsive layouts for desktop and tablet widths. | Must |
| FR-004 | The frontend should support mobile widths for core chat actions. | Should |

### 8.2 Chat and streaming

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-010 | The frontend shall allow users to submit a non-empty chat message. | Must |
| FR-011 | The frontend shall use `POST /v1/chat/stream` as the default chat transport. | Must |
| FR-012 | The frontend shall parse SSE events by event type. | Must |
| FR-013 | The frontend shall concatenate `token` events into the active assistant message. | Must |
| FR-014 | The frontend shall process `session` events and store the session ID. | Must |
| FR-015 | The frontend shall mark a message complete on `done`. | Must |
| FR-016 | The frontend shall show a recoverable error state on `error` events. | Must |
| FR-017 | The frontend shall support fallback to `POST /v1/chat` if streaming is disabled by configuration in the future. | Should |
| FR-018 | The frontend shall not display hidden reasoning or internal prompts. | Must |
| FR-019 | The frontend should show public `thinking` events as progress indicators. | Should |

### 8.3 Sessions

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-030 | The frontend shall list sessions using `GET /v1/sessions`. | Must |
| FR-031 | The frontend shall load session detail using `GET /v1/sessions/{session_id}`. | Must |
| FR-032 | The frontend shall delete sessions using `DELETE /v1/sessions/{session_id}`. | Must |
| FR-033 | The frontend shall handle missing sessions with a not-found state. | Must |
| FR-034 | The frontend should refresh the session list after chat completion and deletion. | Should |
| FR-035 | The frontend shall be designed to support pagination when backend endpoints are added. | Should |

### 8.4 Providers

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-040 | The frontend shall list providers using `GET /v1/providers`. | Must |
| FR-041 | The frontend shall indicate default provider status. | Must |
| FR-042 | The frontend shall indicate provider availability. | Must |
| FR-043 | The frontend shall include the selected provider in chat requests when set. | Must |
| FR-044 | The frontend should discourage selection of unavailable providers. | Should |

### 8.5 Knowledge ingestion

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-050 | The frontend shall provide a text ingestion form. | Must |
| FR-051 | The frontend shall submit knowledge to `POST /v1/knowledge/ingest`. | Must |
| FR-052 | The frontend shall display document ID, chunk count, and status after successful ingestion. | Must |
| FR-053 | The frontend shall validate empty content before submission. | Must |
| FR-054 | The frontend should support structured metadata entry. | Should |

### 8.6 Commands

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-060 | The frontend shall fetch commands from `GET /v1/commands`. | Must |
| FR-061 | The frontend should expose commands through a searchable command palette. | Should |
| FR-062 | The frontend should support keyboard-first command selection. | Should |

### 8.7 Health/status

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-070 | The frontend shall call `/v1/health/live` for liveness status. | Must |
| FR-071 | The frontend shall call `/v1/health/ready` for dependency readiness. | Must |
| FR-072 | The frontend shall render degraded dependency details. | Must |
| FR-073 | The frontend should distinguish backend readiness from provider availability. | Should |

### 8.8 Settings/auth setup

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-080 | The frontend shall support configuring an API base URL for development/self-hosted use. | Must |
| FR-081 | The frontend shall support entering and clearing an API key when backend auth is enabled. | Must |
| FR-082 | The frontend shall attach credentials consistently to protected requests. | Must |
| FR-083 | The frontend shall not hard-code production API secrets. | Must |

## 9. Non-functional requirements

### 9.1 Reliability

- The frontend must tolerate transient network failures and backend 5xx errors without losing the user's draft message.
- The frontend must prevent duplicate submissions caused by repeated clicks while a send is in progress.
- The frontend should preserve local UI state across refreshes where safe, including selected provider and API base URL.
- The frontend should invalidate and refresh server-backed state after mutations.

### 9.2 Maintainability

- The frontend should use generated TypeScript API types from OpenAPI once the frontend project exists.
- API access should be centralized in a typed client layer.
- SSE parsing should be isolated in a reusable module.
- UI components should be separated from data-fetching hooks.
- Feature flags/capability checks should be centralized to avoid scattered backend assumptions.

### 9.3 Compatibility

- The frontend should support current stable versions of Chrome, Edge, Firefox, and Safari.
- The frontend should avoid browser APIs that prevent POST streaming support on Safari unless a tested fallback exists.
- The frontend should be deployable separately from the backend or behind the same origin via a proxy.

### 9.4 Observability

- The frontend should log client-side errors in development.
- Production deployments should support integration with a client error monitoring service.
- API errors should include request IDs when available so users/support can correlate backend logs.
- Timing metrics should be captured for first token, stream duration, and request failures when analytics are introduced.

## 10. Security requirements

### Authentication and secret handling

- The frontend must not embed production API keys in source code, static bundles, or public environment variables.
- Production deployments should use a server-side proxy, session cookies, or short-lived user tokens instead of exposing backend API keys directly to browsers.
- Development mode may support locally entered API keys stored in browser storage, but the UI must make the risk and environment expectation clear.
- The frontend must provide a way to clear locally stored credentials.

### Authorization and permissions

- Administrative features must be hidden or disabled unless the backend exposes a safe authorization/capability signal.
- Memory, knowledge deletion, skill enable/disable, and tool administration should require explicit backend authorization before being exposed.
- Filesystem-related tool information must avoid displaying sensitive paths or denied file contents.

### Input and output safety

- The frontend must treat all model output, tool output, knowledge content, and session content as untrusted.
- Markdown rendering, if used, must sanitize or safely render HTML; raw HTML should be disabled unless sanitized.
- Links in model output should be safe by default, ideally opened with `rel="noopener noreferrer"`.
- Code blocks should be displayed as text and never executed.
- Metadata inputs should enforce reasonable limits consistent with backend validation.

### Transport security

- Production deployments must use HTTPS.
- CORS settings must be explicit for production origins.
- The frontend should not rely on wildcard CORS with credentials.

### Privacy

- The UI should clearly indicate when user content may be sent to external LLM providers.
- Session deletion should clearly state that it deletes persisted session messages, while memory/knowledge deletion semantics require separate backend capabilities.
- Avoid collecting analytics on message content unless explicitly approved and disclosed.

## 11. Performance requirements

### User-perceived performance

- Initial app shell should become interactive quickly enough for local development and demos; target under 2 seconds on a typical development machine after assets are cached.
- Chat submission should show immediate optimistic UI feedback within 100 ms.
- Streaming UI should render the first token as soon as the backend emits it without waiting for stream completion.
- The UI should avoid expensive re-rendering on every token for long messages; batching or efficient state updates may be required.

### API/data performance

- Session list fetching should be cached and invalidated after mutations.
- Session detail should avoid refetch loops during active streaming.
- Provider health should not be polled aggressively because provider checks may be expensive.
- Health checks should be lightweight and use conservative polling intervals.

### Scalability constraints

- The frontend must account for current unpaginated session and message endpoints by avoiding assumptions that the current response shape will scale indefinitely.
- The UI should be architected to add cursor-based pagination without rewriting the message timeline or sidebar.
- Long messages and long sessions should remain usable through virtualization or incremental rendering when needed.

## 12. Accessibility requirements

The frontend should target WCAG 2.2 AA where feasible.

### Keyboard access

- All primary actions must be reachable by keyboard.
- Chat composer must support expected keyboard behavior, including Enter to submit and Shift+Enter for newline if chosen by design.
- Command palette must support keyboard navigation, selection, and dismissal.
- Focus must move predictably after sending messages, opening sessions, deleting sessions, and closing dialogs.

### Screen reader support

- Streaming updates must be announced in a controlled way that does not overwhelm screen reader users.
- Errors must be announced using accessible alert regions.
- Loading and progress states must have text alternatives.
- Icon-only buttons must have accessible labels.

### Visual accessibility

- Text and interactive controls must meet color contrast requirements.
- Focus indicators must be visible.
- The app must not rely on color alone to communicate provider availability, health status, or errors.
- Users should be able to resize text without breaking core chat workflows.

### Motion and timing

- Streaming indicators and animations must respect reduced-motion preferences.
- Time-sensitive UI should not disappear before users can read it.

## 13. Success metrics

### Activation metrics

- Percentage of users who successfully send a first chat message.
- Percentage of users who receive a completed assistant response.
- Time from app load to first message sent.
- Time from first message sent to first visible response token.

### Engagement metrics

- Average messages per session.
- Percentage of users who return to an existing session.
- Number of sessions created per active user/developer environment.
- Provider selector usage rate.

### Knowledge/RAG metrics

- Number of successful knowledge ingestion events.
- Ingestion failure rate by validation vs. system error.
- Percentage of chat sessions after knowledge ingestion.

### Reliability metrics

- Stream error rate.
- Chat request failure rate by HTTP status and backend error code.
- Provider unavailable rate as surfaced by the UI.
- Backend degraded-state exposure frequency.

### Product quality metrics

- User-reported satisfaction with chat responsiveness.
- Number of support/debug reports containing request ID/session ID.
- Accessibility issue count and severity.
- Frontend test coverage for API client, SSE parser, and key chat flows.

## 14. Risks

### Product risks

- Users may expect full ChatGPT-like features such as message editing, file upload, memory management, and rich tool transparency in the first release.
- The initial backend API is sufficient for MVP chat but incomplete for a polished production frontend.
- Lack of knowledge and memory management APIs may make RAG behavior feel opaque.

### Technical risks

- Static API-key authentication is not appropriate for public browser clients.
- POST-based SSE requires custom stream parsing and careful browser compatibility testing.
- Current streaming can degrade to a single final chunk when tools are involved.
- Unpaginated sessions/messages can become slow or unwieldy as usage grows.
- Provider health checks may be slow, costly, or rate-limited if polled frequently.
- In-process backend rate limits and hot cache are not horizontally scalable.

### UX risks

- Thinking/progress events may be misinterpreted as model reasoning if not labeled carefully.
- Tool failures can be confusing if surfaced as raw backend errors.
- Users may not understand when knowledge ingestion affects future answers.
- Degraded health states may be too technical unless translated into user-facing guidance.

### Security risks

- Browser-stored API keys can be copied by users, extensions, or compromised devices.
- Rendering untrusted model output can introduce XSS risk if Markdown/HTML is not handled safely.
- Future tool/skill UI could accidentally expose sensitive filesystem or operational details.

## 15. Assumptions

- The initial frontend will target the existing FastAPI backend routes documented in `docs/frontend-plan.md`.
- The backend will remain the source of truth for session persistence.
- The frontend will be built in TypeScript with React, likely Next.js or Vite + React.
- The backend may require an API key depending on deployment configuration.
- The first frontend version is primarily for developers, product teams, and internal users rather than unauthenticated public consumer traffic.
- The backend API surface will expand over time to support pagination, richer stream metadata, knowledge management, memory management, and tool/skill introspection.
- The product should avoid exposing hidden model chain-of-thought and should only display safe public progress events.

## 16. Constraints

### Backend/API constraints

- Main API routes are mounted under `/v1`.
- Current chat request body supports `message`, optional `provider`, and optional `session_id`.
- Current stream events are limited to `session`, `thinking`, `token`, `done`, and `error`.
- Current session list/detail endpoints are unpaginated.
- Current knowledge API only supports ingestion, not list/detail/delete/search.
- Current provider API only returns name/default/available, not detailed capabilities.
- Current API-key auth is optional and environment-driven.

### Product constraints

- The MVP must work with existing backend endpoints before relying on new backend APIs.
- The frontend should not require backend changes for the first usable chat workflow.
- Documentation and UI should clearly distinguish implemented features from planned features.
- Product design must account for degraded backend dependencies and provider unavailability.

### Engineering constraints

- No frontend code exists yet in the repository.
- The frontend folder structure should avoid mixing Python backend and TypeScript frontend concerns.
- Type generation from OpenAPI should be introduced once the frontend project exists.
- Browser streaming must be implemented with POST-compatible primitives.

## 17. Open questions

1. Should the initial frontend be deployed as a separate web app or served through the FastAPI app?
2. What is the production authentication model: reverse proxy, session cookies, short-lived tokens, or another mechanism?
3. Should provider selection be per message, per session, or global per user?
4. What user-visible name should sessions use before session rename APIs exist?
5. Should knowledge ingestion be available to all users or admin-only?
6. What retention policy applies to sessions, messages, memories, and knowledge documents?
7. What analytics, if any, may collect metadata about user behavior without collecting message content?
8. Which frontend framework should be selected if SSR/server-side auth is required?

## 18. Release readiness checklist

### MVP release blockers

- Chat streaming works with the deployed backend.
- Session list/detail/delete flows work and handle errors.
- Provider selector handles empty, degraded, and unknown-provider cases.
- API key setup or production auth proxy is defined.
- Knowledge ingestion form handles validation and success states.
- Health/status page distinguishes liveness, readiness, and provider availability.
- Basic accessibility review is complete.
- XSS-safe message rendering is confirmed.

### Post-MVP readiness

- Add pagination once backend supports it.
- Add cancellation and run metadata once backend supports it.
- Add knowledge document management once backend supports it.
- Add memory management only after authorization and namespacing are resolved.
- Add frontend integration tests for SSE parsing and critical chat flows.
