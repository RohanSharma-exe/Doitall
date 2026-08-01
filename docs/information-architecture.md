# Doitall Frontend Information Architecture

## Document status

- **Product:** Doitall web frontend
- **Document type:** Information Architecture (IA)
- **Primary source inputs:** `docs/frontend-plan.md`, `docs/product-requirements.md`, and `docs/user-flows.md`
- **Audience:** Product management, product design, frontend engineering, backend engineering, QA, support, and security reviewers
- **Scope:** Browser-based application structure for the Doitall frontend, covering navigation, routes, page hierarchy, search, global actions, breadcrumbs, and contextual panels.

## 1. IA goals and principles

The application IA should make Doitall feel like a transparent agent workspace rather than a generic chat page. The source documents define Chat as the primary workspace while also requiring Knowledge, Dashboard/Status, Memory, Tools & Skills, and Settings surfaces. The IA therefore uses a persistent shell with clear primary navigation, a session-aware chat sidebar, and contextual panels that expose system state without overwhelming users.

### IA principles

1. **Chat-first, platform-aware:** Chat is the default destination because the MVP's fastest path to value is sending or resuming a streamed conversation. Platform surfaces remain visible because provider health, knowledge ingestion, API-key setup, and degraded backend state directly affect chat success.
2. **Current capabilities before future placeholders:** Current API-backed destinations receive full page treatments. Future destinations are visible only when useful for orientation, roadmap clarity, or capability-gated administration.
3. **Operational transparency in the shell:** Backend connectivity, readiness, provider availability, and auth requirements are global concerns, so they appear in persistent navigation/status areas rather than being buried in individual pages.
4. **Context stays near the task:** Chat sessions, provider selection, commands, and progress belong close to the composer. Knowledge ingestion results belong beside the ingestion form. Status details belong beside operational cards.
5. **Progressive disclosure for advanced surfaces:** Memory, tools/skills administration, metrics, raw events, and future account management are secondary or capability-gated to avoid confusing MVP users with unsupported controls.
6. **URL-addressable workspace state:** Active sessions, settings subsections, status panels, and future details should have stable routes so QA, support, and developers can reproduce states with session IDs and direct links.
7. **Accessible navigation model:** The hierarchy must support keyboard navigation, landmarks, skip links, screen-reader friendly status announcements, and predictable focus movement after navigation or destructive actions.

## 2. Navigation hierarchy

```text
App Shell
├── Chat
│   ├── New chat
│   ├── Active session
│   ├── Session history
│   ├── Provider selector
│   └── Command palette
├── Knowledge
│   ├── Text ingestion
│   ├── Ingestion result
│   └── Future: Documents, document detail, retrieval preview, file upload
├── Dashboard / Status
│   ├── Overview
│   ├── Backend health
│   ├── Provider status
│   ├── Diagnostics links
│   └── Future: Metrics, config warnings, audit logs
├── Memory
│   └── Future/capability-gated memory list, search, detail, edit, delete
├── Tools & Skills
│   ├── Commands
│   └── Future/capability-gated tools, skills, execution history, admin controls
└── Settings
    ├── API connection
    ├── API key / development access
    ├── Provider preference
    ├── Appearance and accessibility
    └── Future: Profile, security, workspace, admin settings
```

### Decisions and rationale

- **Chat is first and default** because the MVP requires starting, streaming, persisting, resuming, and deleting chat sessions; this is the primary proof of product value.
- **Knowledge is second** because knowledge ingestion is an MVP capability and directly improves future chat retrieval, but current APIs only support text ingest and success confirmation.
- **Dashboard / Status is a primary destination** because health, readiness, and provider availability are required surfaces and users need operational confidence when chat or ingestion fails.
- **Memory is primary but marked future/capability-gated** because memory management is important to the agent mental model, yet current backend APIs do not expose safe authorized memory controls.
- **Tools & Skills is primary but conservative** because commands are available today and tools/skills are core to Doitall, but live tool timelines and skill administration require new APIs.
- **Settings is primary** because API base URL, API key setup, and provider preference are required for local/self-hosted deployments and auth recovery.
- **Future pages are named in the IA but not shown as active full controls until capabilities exist** so the product has a stable growth path without implying unsupported functionality.

## 3. Sidebar structure

The app uses a two-level sidebar strategy:

1. **Global sidebar:** Persistent primary navigation across the application.
2. **Context sidebar:** Page-specific secondary navigation or records list, most importantly chat session history.

### 3.1 Global sidebar

```text
Doitall
├── Primary nav
│   ├── Chat
│   ├── Knowledge
│   ├── Dashboard
│   ├── Memory
│   ├── Tools & Skills
│   └── Settings
├── Global status summary
│   ├── Backend: Live / Unreachable
│   ├── Readiness: Ready / Degraded
│   └── Providers: Available count / None available
└── Utility actions
    ├── Command palette
    ├── Global search
    └── Help / API docs link
```

#### Decisions and rationale

- **Primary nav remains visible** so users can recover from degraded chat by moving to Status or Settings.
- **Status summary is embedded in the global sidebar** because readiness and provider availability affect every task, especially chat and ingestion.
- **Provider count is shown instead of a detailed list** in the global sidebar to avoid duplicating the provider selector and status page.
- **Command palette and search are utility actions** because they cut across pages and should be keyboard accessible.
- **API docs link belongs in utility/help** because developer diagnostics are important, but `/docs` and `/openapi.json` are backend documentation rather than product destinations.

### 3.2 Chat context sidebar

```text
Chat sidebar
├── New chat button
├── Session filter/search input
├── Session list
│   ├── Active session row
│   ├── Recent sessions
│   └── Empty state: welcome and prompt examples
├── Session row actions
│   ├── Open
│   └── Delete
└── Footer
    ├── Refresh sessions
    └── Current session ID / copy action
```

#### Decisions and rationale

- **New chat is pinned at the top** because creating a session is implicit on first message and should be the fastest action from any existing conversation.
- **Session search/filter is local in MVP** because current session APIs are unpaginated and unsearchable; the control can filter loaded sessions now and later map to `GET /v1/sessions?q=`.
- **Session rows emphasize recency and message count** because the backend exposes these fields today and does not yet expose titles, pins, archive state, or rename metadata.
- **Delete is a row action behind confirmation** because session deletion is supported and destructive.
- **Current session ID is visible/copyable** because developers, QA, and support need reproducible identifiers.

### 3.3 Page-specific sidebars

- **Knowledge:** Show secondary tabs for `Ingest text` now, with disabled/capability-gated placeholders for `Documents`, `Search preview`, and `Uploads`.
- **Dashboard:** Show anchors for `Overview`, `Health`, `Providers`, and `Diagnostics`.
- **Settings:** Show sections for `API connection`, `API key`, `Provider preference`, and `Appearance`.
- **Memory and Tools & Skills:** Show lightweight explanatory navigation only when the backend exposes capabilities; otherwise show roadmap and current command/tool limitations.

## 4. Top navigation

The top navigation is a compact, task-level bar that changes by page while preserving global controls.

```text
Top nav
├── Breadcrumb trail / current page title
├── Page-level primary action
├── Provider selector when relevant
├── Backend readiness badge
├── API key/auth state
├── Global search button
└── Command palette button
```

### Page-specific top nav behavior

| Page | Page title area | Primary action | Right-side controls |
| --- | --- | --- | --- |
| Chat | New chat or session label/session ID | New chat | Provider selector, readiness badge, global search, command palette |
| Knowledge | Knowledge / selected subsection | Ingest text | Readiness badge, global search |
| Dashboard | Dashboard / Status | Refresh status | Last checked time, readiness badge |
| Memory | Memory | Capability-gated search or no-op roadmap CTA | Permission/capability badge |
| Tools & Skills | Tools & Skills | Open commands | Capability badge, command palette |
| Settings | Settings / subsection | Save or test connection | Auth state, readiness badge |

### Decisions and rationale

- **Breadcrumbs share the title area** so users always understand location without needing a separate breadcrumb row.
- **Provider selector appears in Chat top nav and composer context** because provider choice affects the next chat request; a compact top-level display helps users see the active provider before sending.
- **Readiness badge is always visible** because degraded health can explain failures across chat, knowledge, and settings validation.
- **Auth state is visible globally** because protected endpoints may fail from any destination.
- **Command palette remains top-level** because commands assist chat composition today and can become broader app commands later.

## 5. Page hierarchy

### 5.1 Chat

```text
Chat
├── Empty chat state
│   ├── Product explanation
│   ├── Prompt suggestions
│   └── Setup guidance if no providers/auth/backend unavailable
├── Active session
│   ├── Message timeline
│   │   ├── User messages
│   │   ├── Assistant messages
│   │   ├── Safe tool-result messages when present in session history
│   │   ├── Streaming assistant state
│   │   └── Error states
│   ├── Public thinking/progress label
│   ├── Composer
│   │   ├── Message input
│   │   ├── Provider override
│   │   ├── Slash command affordance
│   │   └── Submit/retry state
│   └── Session details context panel
└── Session not found state
```

**Why:** Chat has the deepest hierarchy because it combines the primary workflow, persistent state, streaming state, provider choice, command assistance, and recoverable errors.

### 5.2 Knowledge

```text
Knowledge
├── Text ingestion form
│   ├── Title
│   ├── Content
│   ├── Metadata
│   └── Submit
├── Ingestion result card
│   ├── Document ID
│   ├── Chunk count
│   └── Status
├── Error and validation states
└── Future sections
    ├── Documents
    ├── Document detail/chunks
    ├── File upload
    └── Retrieval search preview
```

**Why:** Current backend supports only ingestion, so the IA keeps management and search as future sections while clearly explaining that ingested knowledge affects future retrieval.

### 5.3 Dashboard / Status

```text
Dashboard / Status
├── Overview status
├── Liveness card
├── Readiness/dependencies card
├── Provider availability cards
├── Diagnostics
│   ├── API base URL
│   ├── FastAPI docs link
│   ├── OpenAPI link
│   └── Latest request/session IDs where available
└── Future admin observability
    ├── Metrics
    ├── Audit logs
    └── Public config/capabilities
```

**Why:** Status is separated from Settings because it answers “is the system working?” while Settings answers “how is this client configured?”

### 5.4 Memory

```text
Memory
├── Capability-gated landing page
├── Future memory list
├── Future memory search
├── Future memory detail
└── Future edit/delete controls
```

**Why:** Memory is conceptually important but must remain disabled or explanatory until APIs, namespacing, and authorization exist.

### 5.5 Tools & Skills

```text
Tools & Skills
├── Commands
│   ├── Command list
│   ├── Search/filter
│   └── Insert into composer guidance
├── Future tool catalog
├── Future skill catalog
├── Future execution history
└── Future admin controls
```

**Why:** Commands are available today and support composer UX; broader tool/skill controls require backend introspection and permission checks.

### 5.6 Settings

```text
Settings
├── API connection
│   ├── Base URL
│   ├── Test connection
│   └── Reset to default
├── API key / development access
│   ├── Enter/replace key
│   ├── Validate key
│   └── Clear key
├── Provider preference
│   ├── Default provider
│   └── Availability warning
├── Appearance and accessibility
│   ├── Theme
│   └── Reduced motion / density future preferences
└── Future account/admin settings
    ├── Profile
    ├── Security
    ├── Workspace
    └── Admin configuration
```

**Why:** Settings combines client-side configuration needed for MVP with future account/admin pages, while making clear that API-key setup is not true user login.

## 6. Route structure

Use stable, semantic routes that can be implemented in Next.js App Router or any React router.

| Route | Page | State | Purpose |
| --- | --- | --- | --- |
| `/` | Redirect to `/chat` | Current | Default to the primary workspace. |
| `/chat` | New chat | Current | Empty composer-focused chat state. |
| `/chat/:sessionId` | Active session | Current | Deep link to persisted session history. |
| `/knowledge` | Knowledge ingest | Current | Text ingestion default. |
| `/knowledge/ingest` | Knowledge ingest | Current | Explicit ingest route; may redirect from `/knowledge`. |
| `/knowledge/documents` | Document list | Future | List/manage ingested documents when APIs exist. |
| `/knowledge/documents/:documentId` | Document detail | Future | Inspect document and chunks. |
| `/knowledge/search` | Retrieval preview | Future | Search knowledge chunks when API exists. |
| `/dashboard` | Status overview | Current/partial | Overall system and provider status. |
| `/dashboard/providers` | Provider status | Current | Detailed provider availability. |
| `/dashboard/health` | Health detail | Current | Liveness/readiness/dependency details. |
| `/memory` | Memory landing | Future/capability-gated | Explain unavailable memory controls or show list. |
| `/memory/:memoryId` | Memory detail | Future | Inspect/edit/delete memory if authorized. |
| `/tools` | Tools & Skills landing | Partial | Commands today; tools/skills later. |
| `/tools/commands` | Commands list | Current | Browse command metadata. |
| `/tools/skills` | Skill catalog | Future | Skills when introspection API exists. |
| `/settings` | Settings overview | Current | Client configuration hub. |
| `/settings/api` | API connection | Current | Configure base URL. |
| `/settings/access` | API key | Current | Enter, validate, clear API key. |
| `/settings/providers` | Provider preference | Current | Set preferred provider. |
| `/settings/appearance` | Appearance | Future/frontend-only | Theme and accessibility preferences. |
| `/login` | Future account login | Future | Only enabled if real account auth exists. |
| `/setup` | Connection setup | Current | Backend unavailable or first-run API connection flow. |

### Decisions and rationale

- **`/chat/:sessionId` instead of query-only state** gives durable, shareable session URLs for QA and support.
- **`/knowledge` defaults to ingestion** because list/search APIs do not exist yet; future document routes are reserved.
- **`/dashboard` is used instead of `/status` as the primary route** because it can grow into operator overview while still presenting status today.
- **`/settings/access` avoids calling API-key setup “login”** because current auth is static API-key configuration, not user identity.
- **Future routes are reserved but should be hidden or disabled unless capability checks pass** to prevent dead-end navigation in MVP.

## 7. Breadcrumbs

Breadcrumbs should appear in the top navigation title area and be keyboard/screen-reader accessible.

### Breadcrumb patterns

| Route | Breadcrumb |
| --- | --- |
| `/chat` | Chat |
| `/chat/:sessionId` | Chat > Session `short-session-id` |
| `/knowledge` or `/knowledge/ingest` | Knowledge > Ingest text |
| `/knowledge/documents/:documentId` | Knowledge > Documents > `short-document-id` |
| `/dashboard` | Dashboard |
| `/dashboard/providers` | Dashboard > Providers |
| `/dashboard/health` | Dashboard > Health |
| `/memory/:memoryId` | Memory > `short-memory-id` |
| `/tools/commands` | Tools & Skills > Commands |
| `/settings/api` | Settings > API connection |
| `/settings/access` | Settings > Development access |
| `/settings/providers` | Settings > Provider preference |

### Decisions and rationale

- **Use short IDs in breadcrumbs** because backend IDs are necessary for debugging but full UUIDs can dominate the header.
- **Prefer entity type labels over inferred titles** because sessions currently lack rename/title support.
- **Breadcrumbs should not replace the session sidebar** because chat navigation depends on scanning recent sessions, not just parent-child location.

## 8. Search behavior

Search should be introduced in layers that match backend capability.

### 8.1 MVP search and filtering

| Scope | Entry point | Backend support | Behavior |
| --- | --- | --- | --- |
| Sessions | Chat sidebar filter | Partial/no backend search | Filter currently loaded session summaries by session ID, agent name, date text, and message count text. |
| Commands | Command palette and Tools > Commands | Current | Fetch `/v1/commands`, cache results, filter client-side by name, description, and usage. |
| Settings | Settings page | Frontend-only | Optional local section search/filter. |

### 8.2 Future global search

Global search should eventually open from `Cmd/Ctrl+K` or the top nav and show grouped results:

```text
Global search
├── Sessions and messages
├── Knowledge documents/chunks
├── Memories
├── Commands
├── Tools and skills
└── Settings/actions
```

### Search decisions and rationale

- **Do not promise global content search in MVP** because session, message, knowledge, and memory search APIs are missing.
- **Offer local session filtering anyway** because unpaginated session lists can become hard to scan even before backend search exists.
- **Command search is first-class** because command metadata is available and keyboard-first command selection is a requirement.
- **Search results are grouped by type in the future** because selecting a session, chunk, memory, or setting has different destinations and permissions.
- **Unauthorized or capability-gated scopes are hidden or labeled unavailable** because frontend search must not imply access to protected data.

## 9. Global actions

Global actions are available from the shell, top nav, keyboard shortcuts, or contextual overflow menus.

| Action | Location | Current/Future | Why it exists |
| --- | --- | --- | --- |
| New chat | Chat sidebar/top nav | Current | Fastest path to value and recovery after deleting an active session. |
| Open command palette | Top nav/keyboard/composer slash | Current | Required command discovery and keyboard workflow. |
| Global search | Top nav/keyboard | Partial/future | Reserved cross-app navigation; MVP can search commands/settings and local sessions. |
| Refresh status | Dashboard/top nav/status badge | Current | Health/provider checks can become stale or recover. |
| Configure API connection | Settings/status error/banner | Current | Backend unreachable/auth failures need immediate remediation. |
| Enter or clear API key | Settings/auth prompt | Current | Required when protected endpoints return 401/403. |
| Select provider | Chat top nav/composer/settings | Current | Provider is request-scoped or preference-scoped and may affect success. |
| Ingest knowledge | Knowledge page/global CTA from empty chat | Current | Adds RAG content and is an MVP feature. |
| Copy session ID | Chat context panel/sidebar/footer | Current | Supports debugging and support. |
| Delete session | Session row/session context | Current | Supported destructive session management. |
| Open API docs | Help/dashboard diagnostics | Current | Developer diagnostics and OpenAPI type generation support. |

### Decisions and rationale

- **Global actions are limited to high-frequency or recovery tasks** so the shell does not become cluttered.
- **Destructive actions are contextual, not global** because delete requires clear object context and confirmation.
- **Provider selection is both local and persistent** because users may override per message/session and also keep a local preferred provider.
- **Knowledge ingest appears as a CTA from empty chat** because no-session empty states should guide users to useful setup steps.

## 10. Context panels

Context panels provide supporting details without forcing users away from the active task.

### 10.1 Chat context panel

```text
Chat context panel
├── Session details
│   ├── Session ID
│   ├── Created at
│   ├── Last accessed
│   └── Message count
├── Provider details
│   ├── Selected provider
│   ├── Default marker
│   └── Availability
├── Stream state
│   ├── Submitting / streaming / complete / failed
│   ├── Public thinking label
│   └── Retry guidance
└── Future debug details
    ├── Run ID
    ├── Model
    ├── Token usage
    ├── Latency
    └── Safe tool timeline
```

**Why:** Developers and QA need session/provider state while chatting, but this information should not interrupt the message timeline.

### 10.2 Knowledge context panel

```text
Knowledge context panel
├── Ingestion constraints
│   ├── Text-only MVP
│   ├── Content length guidance when known
│   └── Metadata key guidance
├── Last ingestion result
│   ├── Document ID
│   ├── Chunk count
│   └── Status
└── Future retrieval explanation
    ├── Search preview
    └── Document management links
```

**Why:** Knowledge ingestion is easy to misunderstand; the panel explains that ingestion affects future chat retrieval and current management APIs are limited.

### 10.3 Dashboard context panel

```text
Dashboard context panel
├── User impact summary
├── Remediation guidance
├── API base URL
├── Docs/OpenAPI links
└── Metrics availability note
```

**Why:** Operators need to translate technical readiness failures into product impact and next steps.

### 10.4 Settings context panel

```text
Settings context panel
├── Security warnings
├── Local/dev API-key explanation
├── Production auth recommendation
└── Current capability summary
```

**Why:** Static browser API keys are risky; the IA keeps the warning near the controls that create the risk.

### 10.5 Memory and Tools context panels

- **Memory:** Explain unavailable APIs, privacy/authorization requirements, and future list/search/edit/delete model.
- **Tools & Skills:** Explain current command metadata, invisible tool execution in chat, and future safe tool event visibility.

**Why:** These surfaces are meaningful for Doitall's agent model, but current backend support is partial; context panels prevent users from mistaking roadmap for shipped controls.

## 11. Responsive behavior

### Desktop and large tablet

- Global sidebar remains visible.
- Chat session sidebar remains visible in Chat.
- Context panels are right-side panels that can collapse.
- Top nav includes breadcrumbs, status, auth, search, and command actions.

### Small tablet and mobile

- Global sidebar collapses to a drawer or bottom navigation.
- Chat session sidebar becomes a drawer opened by “Sessions”.
- Context panels become bottom sheets or route-level detail pages.
- Composer remains sticky at the bottom of Chat.
- Provider selector moves into composer toolbar or a modal sheet.

### Decisions and rationale

- **Chat composer receives layout priority** because sending and reading messages is the core workflow.
- **Sidebars become drawers before removing functionality** because sessions, status, and settings remain necessary on small screens.
- **Context panels collapse by default** because supportive metadata should not crowd the message timeline.

## 12. Capability, permission, and empty-state rules

### Capability rules

- Render **current** features as normal destinations/actions.
- Render **partial** features with explanatory copy and only safe available controls.
- Render **future** features only when capability checks or feature flags explicitly enable them; otherwise show roadmap/empty state if the destination remains visible.
- Hide or disable admin actions unless backend authorization/capability signals exist.

### Empty-state rules

| Empty state | Primary guidance | Secondary actions |
| --- | --- | --- |
| No sessions | Start a first chat with prompt examples. | Configure provider, ingest knowledge, view status. |
| Empty active chat | Focus composer and examples. | Provider selector, command palette. |
| No providers | Explain provider configuration. | Dashboard/Status, Settings/API connection. |
| No commands | Explain commands are unavailable. | Continue typing normally. |
| No knowledge list | Explain text ingestion is available but listing is future. | Ingest text. |
| Backend unavailable | Explain likely connection causes. | Edit API URL, retry. |
| Unauthorized | Explain access key is required. | Enter key, clear key, settings. |
| Memory unavailable | Explain missing APIs and privacy requirements. | Return to Chat or Status. |

### Decisions and rationale

- **Empty states must point to the next useful action** because Doitall's MVP includes several setup-dependent failure modes.
- **Capability gating prevents insecure or misleading UI** for memory, tools/skills administration, metrics, and account settings.
- **Auth failures route to Settings/Access rather than Login** because API-key setup is not account authentication.

## 13. Recommended implementation notes

- Centralize route constants and navigation metadata so labels, breadcrumbs, and capability gates remain consistent.
- Represent navigation items with `current`, `partial`, and `future` status fields.
- Keep route state as the source of truth for active session ID.
- Cache provider and command data conservatively; provider health checks can be expensive.
- Separate global status polling from page-level data fetching.
- Use accessible landmarks: global navigation, complementary session sidebar, main chat/content area, complementary context panel, and status regions.
- Announce streaming and error state changes without overwhelming screen-reader users.
- Avoid using color alone for provider availability, readiness, or errors.

## 14. IA summary

The proposed IA makes Chat the default, session-aware workspace while preserving immediate access to Knowledge ingestion, Dashboard/Status, and Settings because those surfaces directly determine whether the chat experience works. Memory and Tools & Skills are included as durable product concepts but remain capability-gated until safe APIs exist. The combination of global navigation, chat-specific session navigation, compact top navigation, stable routes, cautious search layering, and task-specific context panels gives Doitall a frontend structure that works with current backend endpoints and can grow into the richer roadmap described in the product requirements and user flows.
