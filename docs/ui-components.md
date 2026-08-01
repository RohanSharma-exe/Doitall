# Doitall Frontend UI Component Specification

## Document status

- **Product:** Doitall web frontend
- **Document type:** Complete reusable UI component specification
- **Primary source inputs:** `docs/frontend-plan.md`, `docs/product-requirements.md`, `docs/user-flows.md`, and `docs/information-architecture.md`
- **Audience:** Product design, frontend engineering, backend engineering, QA, accessibility reviewers, and security reviewers
- **Scope:** Reusable UI components for the browser-based Doitall frontend, including foundational primitives, app shell components, chat components, knowledge/status/admin components, feedback components, and page-state components.

## 1. Component design principles

1. **Transparent system state:** Components must expose provider availability, readiness, auth state, streaming state, validation errors, and destructive-action consequences in plain language.
2. **Chat-first reuse:** Components should optimize the Chat workspace first while remaining generic enough for Knowledge, Dashboard/Status, Tools & Skills, Memory, and Settings surfaces.
3. **Capability-aware rendering:** Components that represent partial or future backend capabilities must support disabled, read-only, locked, and roadmap states.
4. **Accessible by default:** Every component must support keyboard access, visible focus, semantic roles, accessible names, non-color-only status communication, and WCAG 2.2 AA-oriented contrast.
5. **Secure output handling:** Components that render model output, tool output, markdown, code, session content, knowledge content, or metadata must treat content as untrusted.
6. **Responsive composition:** Components should support desktop side-by-side layouts, tablet drawers, and mobile bottom sheets without requiring distinct implementations.
7. **Typed API boundaries:** Component props should be serializable and type-friendly so they can be wired to generated OpenAPI types and centralized data hooks later.

## 2. Component taxonomy

```text
Reusable components
├── Foundations
│   ├── Button
│   ├── IconButton
│   ├── ButtonGroup
│   ├── FormField
│   ├── TextInput
│   ├── TextArea
│   ├── SelectInput
│   ├── SearchInput
│   ├── Checkbox
│   ├── RadioGroup
│   ├── Switch
│   ├── MetadataEditor
│   └── KeyboardShortcut
├── Data display
│   ├── Card
│   ├── MetricCard
│   ├── DataTable
│   ├── KeyValueList
│   ├── DescriptionList
│   ├── Badge
│   ├── StatusIndicator
│   ├── ProgressBar
│   ├── LoadingSkeleton
│   └── Timestamp
├── Navigation and layout
│   ├── AppShell
│   ├── GlobalSidebar
│   ├── ContextSidebar
│   ├── TopNav
│   ├── Breadcrumbs
│   ├── Tabs
│   ├── Accordion
│   ├── SplitPane
│   ├── ContextPanel
│   └── Drawer
├── Overlays and feedback
│   ├── Dialog
│   ├── Modal
│   ├── DropdownMenu
│   ├── CommandPalette
│   ├── Toast
│   ├── Alert
│   ├── Tooltip
│   └── Popover
├── Chat and agent workspace
│   ├── ChatComposer
│   ├── MessageTimeline
│   ├── ChatBubble
│   ├── StreamingIndicator
│   ├── ThinkingIndicator
│   ├── ProviderSelector
│   ├── SessionList
│   ├── SessionRow
│   ├── ToolCallTimelineItem
│   ├── ToolCard
│   ├── MemoryCard
│   ├── AgentCard
│   ├── MarkdownRenderer
│   └── CodeBlock
├── Domain forms and cards
│   ├── KnowledgeIngestForm
│   ├── IngestionResultCard
│   ├── ProviderStatusCard
│   ├── HealthStatusCard
│   ├── CommandCard
│   ├── SettingsSection
│   └── ApiConnectionForm
└── Page states
    ├── EmptyState
    ├── ErrorPage
    ├── NotFoundState
    ├── UnauthorizedState
    ├── RateLimitState
    ├── BackendUnavailableState
    └── DegradedModeBanner
```


## Requested component coverage index

This specification explicitly covers Buttons, Inputs, Cards, Tables, Chat bubbles, Code blocks, Markdown renderer, Sidebars, Dialogs, Modals, Dropdowns, Toasts, Alerts, Tabs, Accordions, Tool cards, Memory cards, Agent cards, Status indicators, Progress bars, Loading skeletons, Empty states, and Error pages.

## 3. Shared prop conventions

All components should support these common props unless they are not meaningful for the element.

| Prop | Type | Purpose |
| --- | --- | --- |
| `id` | `string` | Stable DOM or component identifier. |
| `className` | `string` | Styling extension hook. |
| `testId` | `string` | Stable selector for automated tests. |
| `ariaLabel` | `string` | Accessible name for icon-only or ambiguous controls. |
| `disabled` | `boolean` | Prevent interaction and communicate unavailable state. |
| `loading` | `boolean` | Show pending state while preserving layout. |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg'` | Standard scale for controls. |
| `variant` | `string` | Visual/semantic treatment. |
| `tone` | `'neutral' \| 'info' \| 'success' \| 'warning' \| 'danger'` | Status or emphasis tone. |
| `children` | `ReactNode` | Nested content. |

### Shared state names

- **Default:** Ready for normal use.
- **Hover:** Pointer hover affordance.
- **Focus-visible:** Keyboard focus ring.
- **Active/pressed:** Interaction is being activated.
- **Selected/current:** Item represents active route, selected option, or selected record.
- **Disabled:** Unavailable and not actionable.
- **Loading/pending:** An async action is in progress.
- **Error/invalid:** Component or associated data failed validation or request.
- **Readonly:** Value is visible but not editable.
- **Empty:** No data exists for the component.
- **Capability-gated:** Backend capability or permission is unavailable.

## 4. Foundations

### 4.1 Button

**Purpose:** Trigger primary, secondary, destructive, navigation, and inline actions such as send message, retry stream, ingest knowledge, delete session, refresh status, and save settings.

**Props**

| Prop | Type | Notes |
| --- | --- | --- |
| `children` | `ReactNode` | Visible label; required except for icon-only buttons, which should use `IconButton`. |
| `variant` | `'primary' \| 'secondary' \| 'tertiary' \| 'ghost' \| 'danger' \| 'link'` | Visual hierarchy. |
| `size` | `'sm' \| 'md' \| 'lg'` | Layout scale. |
| `type` | `'button' \| 'submit' \| 'reset'` | Native button type. |
| `disabled` | `boolean` | Prevents interaction. |
| `loading` | `boolean` | Shows spinner/progress text and disables duplicate activation. |
| `leftIcon` / `rightIcon` | `IconName` | Optional icon names. |
| `onClick` | `() => void` | Activation handler. |
| `ariaDescribedBy` | `string` | Links to helper or warning text. |

**Variants:** Primary, secondary, tertiary, ghost, danger, link, compact, full-width.

**States:** Default, hover, focus-visible, active, disabled, loading, destructive-confirmed.

**Accessibility:** Use native `<button>`, visible text labels, `aria-busy` when loading, `aria-disabled` only when a non-button fallback is unavoidable, and focus styles that meet contrast requirements. Danger buttons must include text that identifies the object when possible.

**Responsive behavior:** Full-width in narrow forms and dialogs; compact or icon-only only when the label remains available through accessible text or nearby context.

**Interactions:** Enter/Space activate. Loading state prevents duplicate submissions. Destructive actions should open a confirmation dialog unless the action is trivially reversible.

### 4.2 IconButton

**Purpose:** Provide compact actions for session row menus, copy session ID, refresh, close overlays, open drawers, and composer utilities.

**Props:** `icon`, `ariaLabel`, `variant`, `size`, `disabled`, `loading`, `tooltip`, `onClick`.

**Variants:** Ghost, subtle, bordered, danger, selected.

**States:** Default, hover, focus-visible, active, disabled, loading, selected.

**Accessibility:** Requires `ariaLabel`; tooltip is not a substitute for an accessible name. Close buttons should announce the target, such as “Close session details”.

**Responsive behavior:** Minimum touch target of 44 by 44 CSS pixels on touch devices; may use tighter visual icon with padded hit area.

**Interactions:** Supports pointer and keyboard activation; tooltip appears on hover/focus with delay and dismisses on Escape.

### 4.3 ButtonGroup

**Purpose:** Group related actions such as Save/Cancel, Retry/Switch provider, or segmented view choices.

**Props:** `children`, `orientation`, `attached`, `ariaLabel`, `role`, `fullWidthOnMobile`.

**Variants:** Attached segmented controls, separated action row, toolbar group.

**States:** Child button states plus group disabled and overflow-collapsed.

**Accessibility:** Use `role="group"` or toolbar semantics when appropriate. Provide group label for icon-heavy groups.

**Responsive behavior:** Wraps or stacks on small screens; destructive actions should remain visually separated.

**Interactions:** Keyboard traversal follows native tab order unless acting as a roving segmented control.

### 4.4 FormField

**Purpose:** Standard wrapper for labels, descriptions, validation messages, and controls.

**Props:** `label`, `htmlFor`, `description`, `error`, `required`, `optionalText`, `children`, `layout`.

**Variants:** Vertical, horizontal, compact, inline.

**States:** Default, focused child, invalid, disabled, readonly.

**Accessibility:** Connect label, description, and error via `htmlFor`, `aria-describedby`, and `aria-invalid`. Required indicators must be textual or programmatic, not color-only.

**Responsive behavior:** Horizontal layout becomes vertical on mobile.

**Interactions:** Clicking label focuses the input. Error text should appear immediately for client-side validation and after backend validation responses.

### 4.5 TextInput

**Purpose:** Capture short text values such as API base URL, API key, search terms, title, metadata keys, and provider filters.

**Props:** `value`, `defaultValue`, `placeholder`, `type`, `autoComplete`, `maxLength`, `disabled`, `readonly`, `invalid`, `onChange`, `onBlur`, `prefix`, `suffix`, `clearable`.

**Variants:** Default, search, password/secret, monospace, compact.

**States:** Empty, filled, focused, invalid, disabled, readonly, loading validation.

**Accessibility:** Use associated `FormField`; expose validation text; do not rely on placeholder as label. API key fields should support reveal/hide with accessible labels.

**Responsive behavior:** Full-width in forms and drawers; search input can collapse to icon trigger in mobile top nav.

**Interactions:** Optional clear button clears value and returns focus. URL fields validate on blur and on test connection.

### 4.6 TextArea

**Purpose:** Capture long messages, knowledge content, metadata JSON, feedback, and future prompt templates.

**Props:** `value`, `placeholder`, `minRows`, `maxRows`, `autoResize`, `maxLength`, `disabled`, `readonly`, `invalid`, `onChange`, `onKeyDown`, `submitOnEnter`.

**Variants:** Composer, form, monospace, compact.

**States:** Empty, filled, focused, invalid, disabled, readonly, max-length warning.

**Accessibility:** Announce character limits and validation messages. Composer behavior must document Enter vs. Shift+Enter.

**Responsive behavior:** Composer textarea sticks to bottom on mobile and grows only to a safe maximum height.

**Interactions:** In Chat, Enter submits when configured and Shift+Enter inserts newline. During streaming, composer is disabled or guarded.

### 4.7 SelectInput

**Purpose:** Choose providers, settings options, filters, and future model/capability values.

**Props:** `value`, `options`, `placeholder`, `disabled`, `invalid`, `searchable`, `onChange`, `renderOption`, `emptyMessage`.

**Variants:** Native select, custom combobox, compact top-nav select.

**States:** Closed, open, selected, focused, disabled, loading, empty, invalid.

**Accessibility:** Prefer native select for simple lists; custom combobox must implement ARIA combobox/listbox semantics, roving focus, Escape close, and typeahead.

**Responsive behavior:** Custom select can open as a bottom sheet on mobile.

**Interactions:** Disabled/unavailable provider options remain visible with warning text when the user needs context.

### 4.8 SearchInput

**Purpose:** Filter sessions, commands, settings, and future global search results.

**Props:** `value`, `placeholder`, `scope`, `debounceMs`, `loading`, `resultsCount`, `onChange`, `onClear`, `onSubmit`.

**Variants:** Sidebar filter, command palette search, global search, table search.

**States:** Empty, typing, loading, results, no results, error.

**Accessibility:** Label the scope, announce result counts politely, and preserve focus after clearing.

**Responsive behavior:** In mobile navigation, can launch a full-screen command/search overlay.

**Interactions:** Escape clears or closes depending on container. Debounce remote searches when future APIs exist.

### 4.9 Checkbox

**Purpose:** Toggle boolean form options, table row selection, and future admin settings.

**Props:** `checked`, `indeterminate`, `disabled`, `label`, `description`, `onChange`.

**Variants:** Default, card checkbox, table checkbox.

**States:** Unchecked, checked, indeterminate, focused, disabled, invalid.

**Accessibility:** Use native input, programmatic label, and `aria-checked="mixed"` for indeterminate state.

**Responsive behavior:** Label and description wrap beneath the control on narrow screens.

**Interactions:** Space toggles. Table header checkbox toggles visible rows only unless explicitly documented.

### 4.10 RadioGroup

**Purpose:** Choose one option from a small set such as theme preference, provider preference mode, or retry behavior.

**Props:** `value`, `options`, `orientation`, `disabled`, `onChange`, `ariaLabel`.

**Variants:** Standard radios, card radios, segmented radios.

**States:** Unselected, selected, focused, disabled, invalid.

**Accessibility:** Use `fieldset`/`legend` or ARIA radiogroup. Arrow keys move selection when custom rendered.

**Responsive behavior:** Horizontal groups stack vertically on mobile.

**Interactions:** Click/Space selects; card variant selects entire card area.

### 4.11 Switch

**Purpose:** Toggle settings such as advanced mode, reduced motion, dev diagnostics, and future capability flags.

**Props:** `checked`, `label`, `description`, `disabled`, `loading`, `onChange`.

**Variants:** Default, compact, settings row.

**States:** On, off, focused, disabled, loading.

**Accessibility:** Use `role="switch"` or native checkbox with clear on/off label. Do not use switches for destructive or multi-step actions.

**Responsive behavior:** Label remains left and switch right in settings rows; stacks when space is constrained.

**Interactions:** Space toggles. Async toggles use optimistic update only when rollback behavior is defined.

### 4.12 MetadataEditor

**Purpose:** Edit optional knowledge metadata as key/value pairs while respecting backend key-count and shape constraints.

**Props:** `items`, `maxItems`, `keyPlaceholder`, `valuePlaceholder`, `disabled`, `errors`, `onAdd`, `onRemove`, `onChange`, `jsonMode`.

**Variants:** Key-value rows, JSON editor, readonly metadata viewer.

**States:** Empty, editing, invalid key, invalid value, max items reached, readonly, disabled.

**Accessibility:** Each row has labeled key/value fields and remove button with object-specific labels. Errors point to row and field.

**Responsive behavior:** Key/value rows stack on mobile with remove action at row end.

**Interactions:** Add row appends and focuses key input. Remove row asks confirmation only if value is non-empty and form would lose meaningful work.

### 4.13 KeyboardShortcut

**Purpose:** Display shortcut hints such as `Cmd/Ctrl+K`, `Enter`, `Shift+Enter`, and `Esc`.

**Props:** `keys`, `description`, `platform`, `compact`.

**Variants:** Inline, menu hint, help table.

**States:** Default, disabled/unavailable.

**Accessibility:** Provide readable text for screen readers, not only keycap visuals.

**Responsive behavior:** Hide non-critical shortcut hints on mobile where hardware keyboards are less common.

**Interactions:** None; visual helper only.

## 5. Data display components

### 5.1 Card

**Purpose:** Standard container for status summaries, provider cards, ingestion results, settings sections, command cards, memory cards, tool cards, and agent cards.

**Props:** `title`, `subtitle`, `description`, `actions`, `footer`, `tone`, `selected`, `interactive`, `disabled`, `children`.

**Variants:** Default, interactive, selected, compact, elevated, outlined, status-toned.

**States:** Default, hover, focus-visible, selected, disabled, loading, error.

**Accessibility:** Interactive cards need a single clear activation target or well-structured internal controls. Headings should follow page hierarchy.

**Responsive behavior:** Cards stack on mobile and can form responsive grids on desktop.

**Interactions:** If card is clickable, Enter/Space activate. Nested actions must not create ambiguous click targets.

### 5.2 MetricCard

**Purpose:** Display numeric or compact operational values such as provider count, message count, chunk count, stream latency, and future token usage.

**Props:** `label`, `value`, `unit`, `trend`, `tone`, `description`, `loading`, `error`.

**Variants:** Compact, large KPI, status metric.

**States:** Loading, ready, stale, error, unavailable.

**Accessibility:** Include unit and trend in text, not icon/color only.

**Responsive behavior:** Grid columns collapse from 4 to 2 to 1 across breakpoints.

**Interactions:** Optional click drills into detail when a route exists.

### 5.3 DataTable

**Purpose:** Present commands, future knowledge documents, future memories, future audit logs, providers, and settings diagnostics.

**Props:** `columns`, `rows`, `getRowId`, `sortable`, `selectable`, `loading`, `emptyState`, `onSort`, `onRowClick`, `pagination`.

**Variants:** Simple, selectable, sortable, compact, responsive-card.

**States:** Loading, empty, populated, sorted, selected rows, error, capability-gated.

**Accessibility:** Use semantic table markup for tabular data. Sort buttons expose `aria-sort`. Row actions have labels. Selection state is announced.

**Responsive behavior:** On mobile, transform to cards or allow horizontal scroll with sticky first column only when content remains usable.

**Interactions:** Header sort toggles direction. Row click should not conflict with nested buttons or links.

### 5.4 KeyValueList

**Purpose:** Show session IDs, document IDs, created/last accessed timestamps, provider status attributes, and diagnostics.

**Props:** `items`, `copyable`, `monospaceKeys`, `layout`, `emptyMessage`.

**Variants:** Default, compact, bordered, monospace values.

**States:** Populated, empty, copy success, copy failed.

**Accessibility:** Use description list semantics where possible. Copy buttons identify the exact value.

**Responsive behavior:** Values wrap, truncate with copy support, or collapse beneath labels on mobile.

**Interactions:** Copy action triggers toast feedback.

### 5.5 DescriptionList

**Purpose:** Display grouped object details in context panels and detail pages.

**Props:** `sections`, `density`, `bordered`, `actions`.

**Variants:** One-column, two-column, compact.

**States:** Loading, empty, ready.

**Accessibility:** Use `<dl>`, `<dt>`, and `<dd>` semantics.

**Responsive behavior:** Two-column layout becomes one-column on small screens.

**Interactions:** Optional inline copy/edit actions per row.

### 5.6 Badge

**Purpose:** Label default providers, current/partial/future capability states, hidden commands, beta features, auth status, and message roles.

**Props:** `children`, `tone`, `variant`, `size`, `icon`, `ariaLabel`.

**Variants:** Neutral, info, success, warning, danger, outline, filled, pill.

**States:** Default, subtle, emphasized.

**Accessibility:** Badge text must be meaningful; icons are decorative unless conveying additional information via label.

**Responsive behavior:** Truncate long labels with accessible full text.

**Interactions:** Non-interactive by default; if clickable, use Button or link semantics.

### 5.7 StatusIndicator

**Purpose:** Communicate backend liveness, readiness, provider availability, stream status, auth status, ingestion status, and future tool/memory status.

**Props:** `status`, `label`, `description`, `tone`, `showIcon`, `pulse`, `size`.

**Variants:** Dot with label, pill, inline text, card header, nav badge.

**States:** Live, ready, degraded, unavailable, unknown, loading, unauthorized, rate-limited, streaming, complete, failed.

**Accessibility:** Never use color alone; include text label and optional `aria-live` for changing critical statuses.

**Responsive behavior:** Compact dot+label in sidebars; full description in cards and panels.

**Interactions:** Optional click opens Dashboard/Status or details popover.

### 5.8 ProgressBar

**Purpose:** Show determinate or indeterminate progress for ingestion jobs, upload futures, stream pending states, and loading operations.

**Props:** `value`, `max`, `label`, `description`, `indeterminate`, `tone`, `showValue`.

**Variants:** Linear, compact, segmented, inline.

**States:** Idle, running, paused, complete, failed, indeterminate.

**Accessibility:** Use `role="progressbar"` with `aria-valuenow` when determinate; provide textual progress.

**Responsive behavior:** Full-width in forms and cards; compact in table rows.

**Interactions:** None unless paired with cancel/retry controls.

### 5.9 LoadingSkeleton

**Purpose:** Preserve layout while sessions, messages, providers, commands, health, or settings load.

**Props:** `shape`, `lines`, `width`, `height`, `animated`, `label`.

**Variants:** Text lines, card, table, chat bubble, sidebar row, avatar/icon.

**States:** Loading only; should be replaced by ready/empty/error states.

**Accessibility:** Skeletons should usually be `aria-hidden`; parent region announces loading with text. Respect reduced motion.

**Responsive behavior:** Match the eventual component layout at each breakpoint.

**Interactions:** None.

### 5.10 Timestamp

**Purpose:** Render created, last accessed, last checked, message, and ingestion times consistently.

**Props:** `value`, `format`, `relative`, `timezone`, `prefix`, `fallback`.

**Variants:** Relative, absolute, compact, tooltip-with-absolute.

**States:** Valid, missing, invalid, stale.

**Accessibility:** Provide machine-readable `dateTime` and readable exact timestamp, especially when relative text is shown.

**Responsive behavior:** Compact relative format in sidebars; absolute format in detail panels.

**Interactions:** Optional tooltip displays exact timestamp.

## 6. Navigation and layout components

### 6.1 AppShell

**Purpose:** Compose global navigation, top navigation, main content, context sidebars, drawers, global feedback, and status regions.

**Props:** `navItems`, `currentRoute`, `topNav`, `sidebar`, `contextPanel`, `status`, `children`.

**Variants:** Desktop shell, tablet shell, mobile shell, setup shell.

**States:** Loading app config, backend unavailable, unauthorized limited mode, ready, degraded.

**Accessibility:** Provides skip link to main content, semantic landmarks, and a single primary heading per page.

**Responsive behavior:** Global sidebar collapses to drawer/bottom navigation; context panels become drawers or bottom sheets.

**Interactions:** Navigation changes route and moves focus to page heading. Global status changes are announced politely.

### 6.2 GlobalSidebar

**Purpose:** Persistent primary navigation for Chat, Knowledge, Dashboard, Memory, Tools & Skills, and Settings with global status summary and utility actions.

**Props:** `items`, `currentPath`, `statusSummary`, `utilities`, `collapsed`, `onNavigate`, `onToggle`.

**Variants:** Expanded, collapsed rail, mobile drawer.

**States:** Current item, disabled item, capability-gated item, degraded status, offline status.

**Accessibility:** Use `nav` landmark with label. Current route uses `aria-current="page"`. Disabled future items explain why they are unavailable.

**Responsive behavior:** Expanded on desktop, rail at medium widths, drawer or bottom nav on mobile.

**Interactions:** Click/Enter navigates. Utility actions open command palette, global search, or API docs.

### 6.3 ContextSidebar

**Purpose:** Render page-specific secondary navigation or record lists, especially Chat session history.

**Props:** `title`, `actions`, `items`, `selectedId`, `search`, `emptyState`, `footer`, `resizable`, `collapsible`.

**Variants:** Session list, section anchors, settings nav, roadmap nav.

**States:** Loading, empty, populated, filtered, collapsed, error.

**Accessibility:** Use complementary landmark and label. List items expose selection/current state.

**Responsive behavior:** Drawer on tablet/mobile; desktop sidebar can be resizable within constraints.

**Interactions:** Search filters items; selecting item navigates; Escape closes mobile drawer.

### 6.4 TopNav

**Purpose:** Display breadcrumbs/page title, page-level actions, provider selector, readiness badge, auth state, search, and command controls.

**Props:** `breadcrumbs`, `title`, `primaryAction`, `actions`, `status`, `providerSelector`, `authState`.

**Variants:** Standard, chat, setup, minimal.

**States:** Ready, degraded, offline, unauthorized, loading.

**Accessibility:** Header landmark, keyboard reachable actions, status labels not color-only.

**Responsive behavior:** Secondary actions collapse into overflow menu; provider selector moves into composer toolbar on mobile.

**Interactions:** Breadcrumbs navigate; status badge opens Dashboard/Status; auth badge opens Settings/Access.

### 6.5 Breadcrumbs

**Purpose:** Show route hierarchy and provide navigation back to parent sections.

**Props:** `items`, `maxItems`, `separator`, `ariaLabel`.

**Variants:** Full, collapsed, title-integrated.

**States:** Current page, truncated, loading label.

**Accessibility:** Use `nav aria-label="Breadcrumb"`; current item uses `aria-current="page"`.

**Responsive behavior:** Collapse middle items on small screens; preserve current page label.

**Interactions:** Parent crumb activation navigates. Truncated crumbs open dropdown menu.

### 6.6 Tabs

**Purpose:** Switch related subsections such as Knowledge ingest/documents/search, Dashboard overview/providers/health, and Settings sections.

**Props:** `tabs`, `activeValue`, `orientation`, `activationMode`, `onChange`.

**Variants:** Underline, pills, vertical sidebar, compact.

**States:** Active, inactive, focused, disabled, loading count.

**Accessibility:** Implement tablist/tab/tabpanel semantics or use links when each tab maps to a route.

**Responsive behavior:** Horizontal tabs become scrollable or convert to select on mobile.

**Interactions:** Arrow keys move focus; Enter/Space activates when manual activation is used.

### 6.7 Accordion

**Purpose:** Collapse secondary details such as diagnostics, advanced settings, metadata, future tool schemas, and FAQ/help content.

**Props:** `items`, `allowMultiple`, `defaultOpen`, `onToggle`.

**Variants:** Simple, bordered, compact, nested.

**States:** Open, closed, focused, disabled, loading content.

**Accessibility:** Use button headers with `aria-expanded` and `aria-controls`.

**Responsive behavior:** Useful for mobile to reduce vertical complexity; can remain expanded by default on desktop.

**Interactions:** Enter/Space toggles. Optional single-open behavior closes siblings.

### 6.8 SplitPane

**Purpose:** Arrange main content with a resizable context panel or side-by-side inspector.

**Props:** `primary`, `secondary`, `defaultSize`, `minSize`, `maxSize`, `collapsible`, `onResize`.

**Variants:** Horizontal, vertical, fixed, resizable.

**States:** Expanded, collapsed, resizing.

**Accessibility:** Resizer is keyboard accessible with appropriate label and value text.

**Responsive behavior:** Collapses secondary pane into drawer/bottom sheet on small screens.

**Interactions:** Drag or keyboard arrows resize; double-click resets to default size.

### 6.9 ContextPanel

**Purpose:** Show session details, provider details, knowledge guidance, dashboard remediation, settings warnings, and future debug information.

**Props:** `title`, `sections`, `actions`, `open`, `collapsible`, `onClose`, `tone`.

**Variants:** Right panel, inline card, drawer, bottom sheet.

**States:** Open, closed, loading, empty, error, warning.

**Accessibility:** Complementary landmark on desktop; dialog semantics when overlaying mobile content.

**Responsive behavior:** Persistent on desktop, collapsible on tablet, bottom sheet on mobile.

**Interactions:** Close/toggle preserves route and main task state.

### 6.10 Drawer

**Purpose:** Mobile/tablet overlay container for global navigation, session list, filters, or context details.

**Props:** `open`, `side`, `title`, `children`, `onClose`, `modal`, `initialFocus`.

**Variants:** Left, right, bottom, non-modal persistent.

**States:** Opening, open, closing, closed.

**Accessibility:** Modal drawers trap focus; Escape closes; return focus to trigger.

**Responsive behavior:** Replaces sidebars and panels below configured breakpoint.

**Interactions:** Swipe-to-close may be supported if it does not interfere with scrolling.

## 7. Overlays and feedback components

### 7.1 Dialog

**Purpose:** Confirm destructive actions, collect small decisions, or prompt API-key setup without full-page navigation.

**Props:** `open`, `title`, `description`, `children`, `actions`, `onOpenChange`, `initialFocus`, `danger`.

**Variants:** Confirmation, form dialog, alert dialog, non-destructive prompt.

**States:** Open, closed, submitting, error.

**Accessibility:** Use modal dialog semantics, focus trap, labelled title, described body, Escape close unless dangerous submission is in progress.

**Responsive behavior:** Centered on desktop; full-width sheet-like dialog on mobile.

**Interactions:** Primary action submits; Cancel closes; destructive confirmation may require explicit object name for high-risk future actions.

### 7.2 Modal

**Purpose:** Present larger blocking workflows such as API connection setup, future account auth, onboarding, and detailed command/search experiences.

**Props:** `open`, `title`, `size`, `children`, `footer`, `onClose`, `closeOnOverlayClick`.

**Variants:** Small, medium, large, full-screen, wizard.

**States:** Open, loading, submitting, error.

**Accessibility:** Same modal requirements as Dialog; full-screen modals need clear heading and close control.

**Responsive behavior:** Full-screen on mobile for complex forms.

**Interactions:** Prevent accidental close when unsaved changes exist; ask for confirmation before discarding.

### 7.3 DropdownMenu

**Purpose:** Show overflow actions, session row actions, table row actions, user/settings shortcuts, and breadcrumb overflow.

**Props:** `trigger`, `items`, `align`, `side`, `onSelect`.

**Variants:** Standard, checkbox items, radio items, destructive section.

**States:** Closed, open, item focused, item disabled, item danger.

**Accessibility:** Menu semantics, roving focus, Escape close, typeahead for longer menus.

**Responsive behavior:** Converts to bottom sheet for action-heavy menus on touch devices.

**Interactions:** Selecting an item activates and closes unless item is a checkbox/radio that remains open by design.

### 7.4 CommandPalette

**Purpose:** Provide keyboard-first access to commands, navigation, local session filtering, settings sections, and future global search.

**Props:** `open`, `query`, `groups`, `loading`, `emptyState`, `onQueryChange`, `onSelect`, `onClose`.

**Variants:** Commands-only, global search, slash-command insert.

**States:** Empty query, searching, results, no results, loading, error.

**Accessibility:** Combobox/dialog pattern with labelled input, active descendant or roving focus, result count announcements, Escape close.

**Responsive behavior:** Centered modal on desktop; full-screen modal on mobile.

**Interactions:** `Cmd/Ctrl+K` opens global palette; `/` in composer can open command mode; Enter selects highlighted result.

### 7.5 Toast

**Purpose:** Provide transient feedback for copy success, save success, ingestion success, retry started, session deleted, and non-blocking errors.

**Props:** `title`, `description`, `tone`, `duration`, `action`, `onDismiss`.

**Variants:** Info, success, warning, danger, loading/promise.

**States:** Entering, visible, updating, dismissed, action-focused.

**Accessibility:** Use `aria-live` regions; errors should be assertive when immediate attention is needed. Toasts must not be the only place critical information appears.

**Responsive behavior:** Bottom or top stack depending on platform; avoid covering the composer on mobile.

**Interactions:** Dismiss button, optional action button, auto-dismiss for non-critical messages only.

### 7.6 Alert

**Purpose:** Display persistent inline and page-level messages for degraded readiness, unauthorized access, validation errors, provider unavailable, and backend unavailable.

**Props:** `title`, `description`, `tone`, `actions`, `dismissible`, `icon`.

**Variants:** Inline, banner, callout, field-level summary.

**States:** Visible, dismissed, loading action, error action.

**Accessibility:** Use `role="alert"` for urgent errors and `status` for informational updates. Include text labels for tone.

**Responsive behavior:** Banners wrap actions below content on mobile.

**Interactions:** Actions route to Settings, Dashboard, retry, or provider selector.

### 7.7 Tooltip

**Purpose:** Explain icons, truncated IDs, status details, keyboard shortcuts, and disabled controls.

**Props:** `content`, `children`, `side`, `delay`, `disabled`.

**Variants:** Plain, rich, status.

**States:** Hidden, visible, delayed, disabled.

**Accessibility:** Tooltip content should supplement, not replace, accessible names. Dismiss on Escape.

**Responsive behavior:** Avoid hover-only tooltips on touch; use popover or inline helper text when critical.

**Interactions:** Shows on hover/focus, hides on blur/Escape.

### 7.8 Popover

**Purpose:** Show lightweight contextual details such as provider health explanation, status details, date exact values, or quick settings.

**Props:** `open`, `trigger`, `title`, `children`, `placement`, `onOpenChange`.

**Variants:** Non-modal, modal, rich content.

**States:** Closed, open, loading.

**Accessibility:** Manage focus when interactive; label popover content.

**Responsive behavior:** Converts to drawer/bottom sheet if content is complex or screen is narrow.

**Interactions:** Click trigger opens; outside click/Escape closes.

## 8. Chat and agent workspace components

### 8.1 ChatComposer

**Purpose:** Compose and submit chat messages with provider override, command affordance, validation, and streaming guard behavior.

**Props:** `draft`, `provider`, `providers`, `disabled`, `streaming`, `maxLength`, `commandsEnabled`, `onDraftChange`, `onSubmit`, `onProviderChange`, `onOpenCommands`.

**Variants:** Empty-chat composer, active-session composer, compact mobile composer, disabled setup composer.

**States:** Empty, composing, submitting, streaming-disabled, provider unavailable, unauthorized, rate-limited, backend unavailable, validation error.

**Accessibility:** Textarea has label and helper text. Submit button has state-specific accessible label. Streaming state is announced without overwhelming users.

**Responsive behavior:** Sticky bottom on mobile; toolbar wraps below textarea; provider selector moves into modal sheet if needed.

**Interactions:** Enter submits and Shift+Enter inserts newline when configured. Slash opens command suggestions. Submit is blocked for empty or over-limit messages.

### 8.2 MessageTimeline

**Purpose:** Render chronological messages, pending assistant response, safe tool-result history, errors, and retry affordances.

**Props:** `messages`, `loading`, `streamingMessageId`, `error`, `onRetry`, `onCopy`, `virtualized`.

**Variants:** Standard, compact, debug, virtualized long-session.

**States:** Loading, empty, populated, streaming, failed, not found.

**Accessibility:** Use a labelled feed or list. New streaming content should use controlled live regions and avoid announcing every token by default.

**Responsive behavior:** Maintains readable line length on desktop; full-width with safe padding on mobile.

**Interactions:** Copy message, retry failed assistant response, scroll to latest, preserve scroll position when older content loads.

### 8.3 ChatBubble

**Purpose:** Display individual user, assistant, tool-result-safe, system/status, and error messages.

**Props:** `role`, `content`, `status`, `createdAt`, `toolCalls`, `actions`, `markdown`, `error`, `compact`.

**Variants:** User, assistant, tool, system, error, pending, streaming.

**States:** Sending, streaming, complete, failed, copied, retried.

**Accessibility:** Role and timestamp are available to screen readers. Error bubble uses alert semantics when newly created.

**Responsive behavior:** User bubbles can align right on desktop but should use full readable width on small screens. Assistant messages prioritize markdown readability.

**Interactions:** Hover/focus reveals actions. Copy uses toast feedback. Retry appears for failed assistant responses.

### 8.4 StreamingIndicator

**Purpose:** Show stream lifecycle state from `session`, `thinking`, `token`, `done`, and `error` handling.

**Props:** `state`, `label`, `description`, `elapsedMs`, `showSpinner`, `error`.

**Variants:** Inline under bubble, composer status, top-banner compact.

**States:** Connecting, thinking, streaming, finalizing, done, error, disconnected.

**Accessibility:** Use polite live updates for state changes, not every token. Respect reduced motion.

**Responsive behavior:** Inline text wraps under message; compact mode in mobile composer.

**Interactions:** Error state can expose Retry and Switch provider actions.

### 8.5 ThinkingIndicator

**Purpose:** Render safe public thinking/progress events without exposing hidden reasoning.

**Props:** `label`, `steps`, `activeStep`, `tone`, `compact`.

**Variants:** Single label, step list, subtle shimmer-free indicator.

**States:** Waiting, active, complete, failed.

**Accessibility:** Labels must use safe wording such as “Working” or backend-provided public progress. Do not present private chain-of-thought.

**Responsive behavior:** Compact single-line on mobile.

**Interactions:** None except optional expand for public step history when backend supports it.

### 8.6 ProviderSelector

**Purpose:** Choose a provider for a chat request or preferred provider setting while showing default and availability.

**Props:** `providers`, `value`, `defaultProvider`, `loading`, `disabled`, `onChange`, `showUnavailable`, `context`.

**Variants:** Top-nav compact, composer select, settings list, status card picker.

**States:** Loading, available, unavailable, selected, unknown provider error, no providers.

**Accessibility:** Provider status is textual. Unavailable options include explanation. Combobox/select semantics apply.

**Responsive behavior:** Compact menu in top nav; full-screen or bottom sheet picker on mobile.

**Interactions:** Selecting unavailable provider is blocked or warns before proceeding depending on policy. Unknown provider errors route user back to selector.

### 8.7 SessionList

**Purpose:** List persisted chat sessions ordered by recency with local filtering, refresh, empty state, and active-session highlighting.

**Props:** `sessions`, `activeSessionId`, `loading`, `filter`, `error`, `onOpen`, `onDelete`, `onRefresh`, `onFilterChange`.

**Variants:** Sidebar, drawer, compact list.

**States:** Loading, empty, filtered-empty, populated, error, refreshing.

**Accessibility:** Use list semantics. Active session uses `aria-current`. Delete buttons have session-specific labels.

**Responsive behavior:** Sidebar on desktop; drawer on mobile.

**Interactions:** Click/Enter opens session. Delete opens confirmation. Refresh reloads session summaries.

### 8.8 SessionRow

**Purpose:** Represent one session summary with fallback title, last activity, message count, active state, and row actions.

**Props:** `sessionId`, `agentName`, `createdAt`, `lastAccessedAt`, `messageCount`, `active`, `onOpen`, `onDelete`, `actions`.

**Variants:** Default, active, compact, skeleton.

**States:** Default, hover, focus-visible, active/current, deleting, deleted, error.

**Accessibility:** Row is a link or button with clear label. Delete action is separate and labelled.

**Responsive behavior:** ID truncates with copy/tooltip; metadata can move to secondary line.

**Interactions:** Row activates open; overflow menu contains delete/copy ID.

### 8.9 ToolCallTimelineItem

**Purpose:** Future/partial representation of safe tool call and result events in the message timeline.

**Props:** `toolName`, `status`, `summary`, `durationMs`, `startedAt`, `endedAt`, `safeResult`, `error`.

**Variants:** Pending, success, failed, skipped, permission denied.

**States:** Pending, running, complete, failed, redacted.

**Accessibility:** Status is textual and announced when it changes. Sensitive output is never placed in accessible hidden text.

**Responsive behavior:** Collapses technical metadata behind disclosure on mobile.

**Interactions:** Expand/collapse safe details; copy safe result if allowed.

### 8.10 ToolCard

**Purpose:** Present a tool or skill capability in Tools & Skills, future catalog, or safe tool timeline detail.

**Props:** `name`, `description`, `status`, `version`, `permissions`, `schema`, `enabled`, `capabilityState`, `actions`.

**Variants:** Catalog card, compact chip, timeline card, admin card.

**States:** Enabled, disabled, unavailable, running, failed, capability-gated, permission-required.

**Accessibility:** Permissions and status are text. Admin toggles are labelled and disabled without permission.

**Responsive behavior:** Cards form grid on desktop and stack on mobile; schema details collapse.

**Interactions:** Open details, copy schema, future enable/disable with confirmation and authorization enforcement.

### 8.11 MemoryCard

**Purpose:** Future memory list/detail component for safe authorized memory viewing.

**Props:** `memoryId`, `contentPreview`, `score`, `source`, `scope`, `createdAt`, `updatedAt`, `permissions`, `actions`.

**Variants:** List card, detail card, search result, redacted.

**States:** Normal, selected, redacted, stale, editing, deleting, capability-gated.

**Accessibility:** Clearly identify memory scope and privacy status. Redacted content should state why it is hidden.

**Responsive behavior:** Metadata wraps below preview on mobile.

**Interactions:** Open detail, future edit/delete with confirmation, copy ID.

### 8.12 AgentCard

**Purpose:** Represent an agent/workspace capability such as Doitall agent identity, future agent catalog, or session agent metadata.

**Props:** `name`, `description`, `status`, `provider`, `capabilities`, `avatar`, `actions`.

**Variants:** Compact identity card, catalog card, status card.

**States:** Active, inactive, degraded, unavailable, selected.

**Accessibility:** Avatar is decorative unless it conveys unique information; status label is textual.

**Responsive behavior:** Compact in sidebars, full in catalog grids.

**Interactions:** Select/open agent detail when multiple agents are supported in future.

### 8.13 MarkdownRenderer

**Purpose:** Safely render assistant messages, documentation snippets, command descriptions, and knowledge previews.

**Props:** `content`, `allowedElements`, `disallowHtml`, `linkTarget`, `components`, `codeBlockRenderer`, `compact`.

**Variants:** Chat message, documentation, compact preview, sanitized rich text.

**States:** Rendering, rendered, parse error, empty.

**Accessibility:** Preserve heading order inside the surrounding page, provide accessible links, and expose code blocks with language labels.

**Responsive behavior:** Tables and wide content scroll horizontally within message bounds; images are constrained if ever allowed.

**Interactions:** Links open safely with `rel="noopener noreferrer"`; code blocks use CodeBlock actions.

### 8.14 CodeBlock

**Purpose:** Render code, commands, JSON payloads, SSE examples, and model-generated snippets safely.

**Props:** `code`, `language`, `filename`, `highlightLines`, `wrap`, `copyable`, `maxHeight`.

**Variants:** Inline code, block code, terminal command, JSON, diff.

**States:** Default, copied, copy failed, expanded/collapsed.

**Accessibility:** Language label and copy button are accessible. Code remains selectable text and is never executed.

**Responsive behavior:** Horizontal scroll or soft-wrap toggle. Long blocks collapse with “Show more”.

**Interactions:** Copy to clipboard, wrap toggle, expand/collapse.

## 9. Domain forms and cards

### 9.1 KnowledgeIngestForm

**Purpose:** Submit text knowledge documents with title, content, and optional metadata to the ingestion endpoint.

**Props:** `title`, `content`, `metadata`, `submitting`, `limits`, `errors`, `onSubmit`, `onChange`, `onReset`.

**Variants:** Full page, compact onboarding CTA, admin form.

**States:** Empty, dirty, validating, submitting, success, validation error, backend error, rate-limited.

**Accessibility:** Field-level validation, submit status, and success/error summaries are announced.

**Responsive behavior:** Single column on mobile; metadata editor can be collapsed.

**Interactions:** Prevent empty content submission; success shows IngestionResultCard; dirty state warns before navigation if content would be lost.

### 9.2 IngestionResultCard

**Purpose:** Confirm successful knowledge ingestion with document ID, chunk count, and status.

**Props:** `documentId`, `chunkCount`, `status`, `metadata`, `actions`.

**Variants:** Success, warning partial, failed, compact.

**States:** Success, failed, pending/future job, copied document ID.

**Accessibility:** Success/failure is text and live-announced after submission.

**Responsive behavior:** Actions wrap beneath content on mobile.

**Interactions:** Copy document ID, start another ingestion, go to Chat.

### 9.3 ProviderStatusCard

**Purpose:** Show provider name, default marker, availability, and guidance.

**Props:** `name`, `available`, `isDefault`, `description`, `lastCheckedAt`, `actions`.

**Variants:** Available, unavailable, default, selected, compact.

**States:** Loading, available, unavailable, unknown, selected.

**Accessibility:** Availability is text; default marker is labelled.

**Responsive behavior:** Provider cards grid on desktop and stack on mobile.

**Interactions:** Select provider, open diagnostics, refresh providers.

### 9.4 HealthStatusCard

**Purpose:** Show liveness, readiness, and dependency status for Dashboard/Status and global summaries.

**Props:** `service`, `status`, `details`, `lastCheckedAt`, `impact`, `actions`.

**Variants:** Liveness, readiness, dependency, compact summary.

**States:** Healthy, degraded, unavailable, loading, stale, error.

**Accessibility:** Status and impact are text. Critical degraded states use alerts when newly detected.

**Responsive behavior:** Cards stack and details collapse on mobile.

**Interactions:** Refresh, expand details, open remediation links.

### 9.5 CommandCard

**Purpose:** Display slash-command metadata in Tools & Skills or CommandPalette results.

**Props:** `name`, `description`, `usage`, `hidden`, `onInsert`, `onCopy`.

**Variants:** List item, card, palette result, hidden/dev.

**States:** Default, focused, selected, hidden, copied, unavailable.

**Accessibility:** Command name and usage are readable; insert action explains it will not submit automatically.

**Responsive behavior:** Usage wraps in monospace block on narrow screens.

**Interactions:** Insert into composer, copy usage, filter by query.

### 9.6 SettingsSection

**Purpose:** Group related settings with heading, description, controls, save/cancel state, and security guidance.

**Props:** `title`, `description`, `children`, `actions`, `dirty`, `saving`, `error`, `warning`.

**Variants:** API connection, access key, provider preference, appearance, admin future.

**States:** Clean, dirty, saving, saved, error, disabled, capability-gated.

**Accessibility:** Section heading, form semantics, error summary.

**Responsive behavior:** Controls stack and action row becomes sticky in long mobile forms only when helpful.

**Interactions:** Save, cancel, test, clear key, reset to default.

### 9.7 ApiConnectionForm

**Purpose:** Configure API base URL and development API key behavior for local/self-hosted deployments.

**Props:** `baseUrl`, `apiKey`, `authRequired`, `testing`, `errors`, `onTest`, `onSave`, `onClearKey`.

**Variants:** Setup page, settings section, unauthorized prompt.

**States:** Empty, valid URL, invalid URL, testing, reachable, unreachable, unauthorized, saved.

**Accessibility:** Security warning is associated with API key field. Test results are announced.

**Responsive behavior:** Full-width form on setup/mobile; inline test/save actions stack.

**Interactions:** Test connection calls public/protected endpoints as appropriate; clear key requires confirmation if currently authenticated.

## 10. Page-state components

### 10.1 EmptyState

**Purpose:** Guide users when there are no sessions, commands, providers, knowledge documents, memories, or search results.

**Props:** `title`, `description`, `illustration`, `primaryAction`, `secondaryActions`, `tone`, `scope`.

**Variants:** No sessions, empty chat, no providers, no commands, no knowledge list, no memories, no search results.

**States:** Informational, setup-required, capability-gated, filtered-empty.

**Accessibility:** Uses a heading and descriptive text. Actions are keyboard reachable.

**Responsive behavior:** Centered in available space but avoids pushing composer off-screen in Chat.

**Interactions:** Primary action routes to next useful step such as Start chat, Configure provider, Ingest knowledge, or View status.

### 10.2 ErrorPage

**Purpose:** Display full-page unrecoverable or route-level errors.

**Props:** `statusCode`, `title`, `description`, `requestId`, `actions`, `details`, `tone`.

**Variants:** Generic error, backend unavailable, unauthorized, not found, rate limited, degraded.

**States:** Visible, retrying, details expanded.

**Accessibility:** Main heading describes error. Critical errors use appropriate alert semantics without trapping focus.

**Responsive behavior:** Actions stack on mobile; technical details collapse.

**Interactions:** Retry, go to Chat, open Settings, copy request/session ID, expand diagnostics.

### 10.3 NotFoundState

**Purpose:** Handle invalid or deleted session routes and future missing documents/memories.

**Props:** `resourceType`, `resourceId`, `actions`, `onRetry`.

**Variants:** Session not found, document not found, memory not found, route not found.

**States:** Missing, checking, already deleted.

**Accessibility:** Clear heading and next actions.

**Responsive behavior:** Same as ErrorPage.

**Interactions:** Start new chat, return to list, refresh.

### 10.4 UnauthorizedState

**Purpose:** Explain missing or invalid API key and route users to development access setup.

**Props:** `message`, `returnTo`, `onConfigure`, `onRetry`, `onClearKey`.

**Variants:** Inline alert, modal prompt, full page.

**States:** Missing key, invalid key, expired future auth, validating.

**Accessibility:** Error is announced; API key prompt uses labelled fields.

**Responsive behavior:** Modal becomes full-screen setup on mobile.

**Interactions:** Configure key, clear key, retry protected request.

### 10.5 RateLimitState

**Purpose:** Communicate 429 responses for chat, ingestion, or other protected endpoints.

**Props:** `retryAfter`, `scope`, `onRetry`, `message`.

**Variants:** Inline composer warning, form alert, full-page limit.

**States:** Limited, countdown, retry-ready.

**Accessibility:** Countdown updates should not be announced every second unless user focuses it.

**Responsive behavior:** Inline warning wraps above composer/form actions.

**Interactions:** Retry disabled until countdown when retry-after exists.

### 10.6 BackendUnavailableState

**Purpose:** Guide users when the API cannot be reached or health checks fail.

**Props:** `baseUrl`, `causes`, `onEditUrl`, `onRetry`, `diagnostics`.

**Variants:** Setup page, banner, inline card.

**States:** Offline, retrying, wrong URL, CORS suspected, recovered.

**Accessibility:** Clear problem statement and labelled URL controls.

**Responsive behavior:** Full setup screen on first load; compact banner in app shell after initial load.

**Interactions:** Edit API URL, retry connection, open setup docs/API docs if available.

### 10.7 DegradedModeBanner

**Purpose:** Persistently communicate readiness degradation while allowing unaffected surfaces to remain usable.

**Props:** `status`, `affectedServices`, `impact`, `actions`, `dismissible`.

**Variants:** Warning banner, critical banner, compact nav badge.

**States:** Degraded, unavailable, dismissed, refreshed/recovered.

**Accessibility:** Use status/alert semantics depending on severity. Impact must be textual.

**Responsive behavior:** Actions wrap to second line on mobile; banner should not obscure composer.

**Interactions:** View Dashboard, refresh status, dismiss non-critical warning.

## 11. Cross-component interaction rules

### 11.1 Chat submission

- `ChatComposer` validates non-empty message and provider availability.
- `Button` enters loading or disabled state immediately on submit.
- `MessageTimeline` receives optimistic user message and pending assistant `ChatBubble`.
- `StreamingIndicator` shows connecting, thinking, streaming, done, or error states.
- `SessionList` refreshes after stream completion or deletion.
- `Toast` is reserved for secondary feedback; critical stream errors appear inline in the timeline.

### 11.2 Provider selection

- `ProviderSelector` displays unavailable providers with text explanations.
- `StatusIndicator` and `ProviderStatusCard` share the same status vocabulary.
- Unknown provider errors route focus back to `ProviderSelector` and show an inline `Alert`.

### 11.3 Knowledge ingestion

- `KnowledgeIngestForm` owns field validation and submission state.
- `MetadataEditor` enforces key/value shape and count limits where known.
- `IngestionResultCard` appears after success and offers copy and “Go to Chat” actions.
- Validation failures use field errors plus optional form-level `Alert`.

### 11.4 Auth and connection recovery

- Protected endpoint failures trigger `UnauthorizedState` or API-key `Dialog`.
- Backend network failures trigger `BackendUnavailableState` and global degraded/offline status.
- Settings and setup forms should return users to their previous route after successful recovery.

### 11.5 Destructive actions

- Session delete uses `Dialog` confirmation, `Button` danger variant, `Toast` success, and `SessionList` refresh.
- Future memory/document/tool admin destructive actions must include object name, permission check, confirmation, and recoverable error handling.

## 12. Responsive and accessibility baseline

### Responsive baseline

| Breakpoint | Behavior |
| --- | --- |
| Desktop | Global sidebar, context sidebar, top nav, main content, and optional context panel can be visible simultaneously. |
| Large tablet | Global sidebar may collapse to rail; context sidebar remains available or collapses based on content width. |
| Small tablet | Global/sidebar/context panels become drawers; top nav actions collapse to overflow. |
| Mobile | Composer remains sticky; sidebars are drawers; complex modals become full-screen; tables become cards or horizontal scroll containers. |

### Accessibility baseline

- All interactive components support keyboard operation.
- Focus order follows visual/task order.
- Focus returns to the triggering control after overlays close.
- Loading, error, success, and streaming state changes use appropriate live-region behavior.
- Color is never the only indicator of status, selection, validation, or availability.
- Icon-only controls require accessible names.
- Markdown and model output are sanitized and rendered without executing HTML or scripts.
- Motion respects `prefers-reduced-motion`.

## 13. Component priority by release phase

| Phase | Components |
| --- | --- |
| MVP Chat | Button, IconButton, FormField, TextArea, SelectInput, SearchInput, AppShell, GlobalSidebar, ContextSidebar, TopNav, Breadcrumbs, ChatComposer, MessageTimeline, ChatBubble, StreamingIndicator, ProviderSelector, SessionList, SessionRow, MarkdownRenderer, CodeBlock, Alert, Toast, Dialog, EmptyState, ErrorPage, StatusIndicator, LoadingSkeleton. |
| Knowledge and Status | KnowledgeIngestForm, MetadataEditor, IngestionResultCard, ProviderStatusCard, HealthStatusCard, MetricCard, KeyValueList, DataTable, Tabs, Accordion, ContextPanel, DegradedModeBanner, BackendUnavailableState, UnauthorizedState, RateLimitState. |
| Tools, Memory, and Admin | CommandPalette, CommandCard, ToolCard, ToolCallTimelineItem, MemoryCard, AgentCard, ApiConnectionForm, SettingsSection, Modal, DropdownMenu, Popover, Drawer, ProgressBar, NotFoundState. |

## 14. Implementation notes

- Prefer composition over large one-off page components. For example, `ProviderStatusCard` should compose `Card`, `StatusIndicator`, `Badge`, and `Timestamp`.
- Keep status vocabulary centralized so provider, health, stream, ingestion, and tool states use consistent tone and labels.
- Keep variant names semantic rather than purely visual, such as `danger`, `degraded`, `streaming`, and `capability-gated`.
- Place API-aware behavior in hooks and containers; reusable components should receive typed props and callbacks.
- Use generated OpenAPI types for API-derived props when the frontend project exists, but keep presentation components decoupled from fetch details.
- Snapshot and interaction-test critical components: `ChatComposer`, `MessageTimeline`, `ProviderSelector`, `SessionList`, `KnowledgeIngestForm`, `CommandPalette`, `Dialog`, and all page-state components.
