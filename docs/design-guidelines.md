# Doitall Figma Design Guidelines

## Document status

- **Product:** Doitall web frontend
- **Document type:** Figma visual design guidelines
- **Primary source inputs:** `docs/frontend-plan.md`, `docs/product-requirements.md`, `docs/user-flows.md`, `docs/information-architecture.md`, and `docs/ui-components.md`
- **Audience:** Product design, visual design, frontend engineering, QA, accessibility reviewers, and product stakeholders
- **Scope:** Visual language, layout rules, design tokens, responsive behavior, interaction patterns, and state guidance for designing Doitall as a premium AI platform in Figma.

## 1. Creative direction

Doitall should feel like a premium AI platform for builders and operators: calm, precise, trustworthy, fast, and technically capable. The product should feel familiar to users of modern AI and productivity tools, but the visual language must be original and owned by Doitall.

### Inspiration without copying

| Inspiration | What to learn | What not to copy |
| --- | --- | --- |
| ChatGPT | Conversational clarity, minimal chat chrome, readable message composition. | Do not copy exact chat layout, iconography, message styling, or green brand associations. |
| Claude | Warm editorial feel, humane empty states, calm writing surface. | Do not copy typography treatment, color warmth, or artifact metaphors. |
| Cursor | Developer confidence, command-first workflows, code readability. | Do not copy editor chrome, dark palette, or command palette visuals directly. |
| Linear | Precision, density control, excellent keyboard interaction, refined motion. | Do not copy sidebar structure, gradients, issue/status styling, or monochrome brand system. |
| Vercel | Premium technical polish, clean contrast, deploy/status confidence. | Do not copy black-and-white identity, card composition, or dashboard treatment. |
| Notion | Approachable productivity, composable content, lightweight surfaces. | Do not copy document blocks, sidebar affordances, or icon style. |

### Original visual language: “Quiet Intelligence”

The Doitall visual system is named **Quiet Intelligence**.

It combines:

1. **Graphite precision:** Neutral graphite surfaces, crisp borders, and measured spacing for developer trust.
2. **Aurora intelligence:** Subtle blue-violet-cyan accent light used sparingly for AI activity, focus, streaming, and command experiences.
3. **Layered glass depth:** Soft translucent panels and restrained shadows that feel premium without becoming decorative noise.
4. **Human-readable density:** Generous message reading space with compact operational panels for providers, status, sessions, and diagnostics.
5. **State transparency:** Every visual treatment should help users understand what is ready, degraded, streaming, blocked, or recoverable.

## 2. Figma setup

### Files and pages

Create one Figma file named **Doitall Frontend Design System** with these pages:

1. **00 Cover** — product mood, principles, links, and version history.
2. **01 Foundations** — typography, color, spacing, radius, elevation, shadows, iconography, motion tokens.
3. **02 Components** — reusable components mapped to `docs/ui-components.md`.
4. **03 Patterns** — chat, knowledge ingestion, status, settings, command palette, auth recovery, empty/error states.
5. **04 Responsive** — desktop, tablet, and mobile layouts.
6. **05 Prototypes** — primary user flows and micro-interaction prototypes.
7. **99 Archive** — deprecated explorations and references.

### Figma variables

Use Figma variables for:

- Color modes: `Light`, `Dark`, and `High Contrast` future mode.
- Spacing scale.
- Radius scale.
- Shadow/elevation tokens.
- Text styles.
- Motion duration/easing annotations.
- Component density: `Comfortable`, `Compact` future mode.

### Naming convention

Use slash-based token naming:

```text
color/surface/base
color/text/primary
space/4
radius/lg
shadow/elevation-2
type/body/md
motion/duration/fast
component/button/height/md
```

## 3. Typography

### Typeface direction

Use a modern, neutral grotesk for the interface and a high-quality monospaced face for code, IDs, commands, and API payloads.

Recommended implementation stack:

- **Primary UI:** Inter, Geist Sans, or a similar open neutral sans.
- **Mono:** JetBrains Mono, Geist Mono, or a similar highly legible monospaced typeface.
- **Fallbacks:** `system-ui`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `sans-serif`; mono fallback `ui-monospace`, `SFMono-Regular`, `Menlo`, `monospace`.

### Typographic personality

- Interface type should be **calm and exact**, not playful.
- AI/chat content should be **reader-friendly**, with slightly more line height than dense operational UI.
- Diagnostics and IDs should be **monospaced but subdued**, supporting debugging without visually dominating the page.

### Type scale

| Token | Size | Line height | Weight | Usage |
| --- | --- | --- | --- | --- |
| `type/display/lg` | 40 | 48 | 650 | Marketing/onboarding hero only. |
| `type/display/md` | 32 | 40 | 650 | Empty state hero, setup screen headings. |
| `type/heading/xl` | 28 | 36 | 650 | Page titles on desktop. |
| `type/heading/lg` | 24 | 32 | 650 | Major panels and modal titles. |
| `type/heading/md` | 20 | 28 | 620 | Section headings and cards. |
| `type/heading/sm` | 16 | 24 | 620 | Sidebar group labels, compact card headings. |
| `type/body/lg` | 17 | 28 | 400 | Assistant message body, long-form markdown. |
| `type/body/md` | 15 | 24 | 400 | Default UI copy and user messages. |
| `type/body/sm` | 14 | 20 | 400 | Secondary UI, descriptions, menus. |
| `type/body/xs` | 12 | 16 | 450 | Badges, metadata, timestamps. |
| `type/label/md` | 13 | 16 | 560 | Buttons, inputs, tabs, table headers. |
| `type/mono/md` | 13 | 20 | 400 | Code blocks, commands, JSON. |
| `type/mono/sm` | 12 | 18 | 400 | Session IDs, request IDs, metadata. |

### Typography rules

- Use `type/body/lg` for assistant responses so answers feel premium and readable.
- Use `type/body/md` for user bubbles, forms, and general content.
- Use `type/body/sm` and `type/body/xs` for operational metadata.
- Avoid more than two font weights in a single component.
- Headings use slight negative letter spacing only at 24 px and above.
- Never use all caps for long labels; reserve uppercase only for compact technical tags when readability is preserved.
- Code and IDs should never use the proportional UI font.

## 4. Color palette

### Color strategy

Doitall uses a neutral graphite foundation with a distinctive aurora accent system. Accent colors should feel like intelligence moving through a technical interface: precise, luminous, and restrained.

### Core brand colors

| Token | Light | Dark | Usage |
| --- | --- | --- | --- |
| `brand/aurora-500` | `#635BFF` | `#8B7CFF` | Primary actions, focus accents, active nav. |
| `brand/aurora-600` | `#5146E8` | `#A79BFF` | Hover/pressed primary actions. |
| `brand/cyan-500` | `#08A9C9` | `#28D4F4` | Streaming, live, connective AI activity. |
| `brand/iris-500` | `#7C3AED` | `#B28CFF` | Command palette and agent intelligence accents. |
| `brand/mint-500` | `#10A37F` | `#37D6A3` | Success and completion highlights. |

### Neutral palette

| Token | Light | Dark | Usage |
| --- | --- | --- | --- |
| `neutral/0` | `#FFFFFF` | `#050608` | Page background extremes. |
| `neutral/50` | `#F8FAFC` | `#0A0D12` | App background. |
| `neutral/100` | `#F1F5F9` | `#111620` | Subtle surfaces. |
| `neutral/200` | `#E2E8F0` | `#1C2430` | Borders, dividers. |
| `neutral/300` | `#CBD5E1` | `#2A3444` | Strong borders, disabled outlines. |
| `neutral/500` | `#64748B` | `#94A3B8` | Secondary text. |
| `neutral/700` | `#334155` | `#CBD5E1` | Body text. |
| `neutral/900` | `#0F172A` | `#F8FAFC` | Primary text. |

### Semantic palette

| Token | Light | Dark | Usage |
| --- | --- | --- | --- |
| `success` | `#0E9F6E` | `#34D399` | Ready, complete, ingested, copied. |
| `warning` | `#B7791F` | `#FBBF24` | Degraded, rate-limited, caution. |
| `danger` | `#DC2626` | `#F87171` | Failed, destructive, invalid. |
| `info` | `#2563EB` | `#60A5FA` | Neutral guidance and diagnostics. |
| `live` | `#0891B2` | `#22D3EE` | Streaming, liveness, active connection. |

### Light mode color roles

| Role | Token | Value |
| --- | --- | --- |
| Page background | `color/surface/page` | `#F8FAFC` |
| App shell | `color/surface/shell` | `#FFFFFF` |
| Raised panel | `color/surface/raised` | `#FFFFFF` |
| Subtle panel | `color/surface/subtle` | `#F1F5F9` |
| Input surface | `color/surface/input` | `#FFFFFF` |
| Primary text | `color/text/primary` | `#0F172A` |
| Secondary text | `color/text/secondary` | `#475569` |
| Tertiary text | `color/text/tertiary` | `#64748B` |
| Border subtle | `color/border/subtle` | `#E2E8F0` |
| Border strong | `color/border/strong` | `#CBD5E1` |
| Focus ring | `color/focus/ring` | `#8B7CFF` |

### Dark mode color roles

| Role | Token | Value |
| --- | --- | --- |
| Page background | `color/surface/page` | `#050608` |
| App shell | `color/surface/shell` | `#0A0D12` |
| Raised panel | `color/surface/raised` | `#111620` |
| Subtle panel | `color/surface/subtle` | `#151B26` |
| Input surface | `color/surface/input` | `#0D121A` |
| Primary text | `color/text/primary` | `#F8FAFC` |
| Secondary text | `color/text/secondary` | `#CBD5E1` |
| Tertiary text | `color/text/tertiary` | `#94A3B8` |
| Border subtle | `color/border/subtle` | `#1C2430` |
| Border strong | `color/border/strong` | `#2A3444` |
| Focus ring | `color/focus/ring` | `#A79BFF` |

### Gradients

Use gradients sparingly. They should signal AI activity or premium focus, not decorate every surface.

| Token | Stops | Usage |
| --- | --- | --- |
| `gradient/aurora-line` | `#635BFF -> #08A9C9 -> #7C3AED` | Thin active rule, command palette accent, streaming edge. |
| `gradient/aurora-glow` | translucent violet/cyan radial glows | Empty state hero, setup background, command palette backdrop. |
| `gradient/surface-glass` | transparent white/dark overlay | Elevated panels in dark mode. |

### Color rules

- Primary brand color should appear on primary buttons, active navigation, focus accents, and selected states only.
- Streaming states use cyan/live accents, not primary purple, so users can distinguish “AI is working” from “user-selected”.
- Warning and danger colors require text labels and icons; never rely on color alone.
- Dark mode should avoid pure black surfaces except the page background; cards and panels need visible layering.
- Light mode should feel airy but not washed out; borders and shadows should define hierarchy without heavy gray blocks.

## 5. Spacing

### Spacing scale

Use a 4 px base spacing scale.

| Token | Value | Usage |
| --- | --- | --- |
| `space/0` | 0 | Reset. |
| `space/1` | 4 | Tight gaps, icon offsets. |
| `space/2` | 8 | Small control gaps, badge padding. |
| `space/3` | 12 | Form helper spacing, menu item gaps. |
| `space/4` | 16 | Default component padding and grid gutters. |
| `space/5` | 20 | Card inner rhythm. |
| `space/6` | 24 | Section spacing and panel padding. |
| `space/8` | 32 | Page sections, modal padding. |
| `space/10` | 40 | Major layout separation. |
| `space/12` | 48 | Empty state and hero rhythm. |
| `space/16` | 64 | Large page-level spacing. |
| `space/20` | 80 | Hero/setup spacing only. |

### Spacing rules

- Use 16 px as the default component gap.
- Use 24 px as the default panel/card padding on desktop.
- Use 16 px panel padding on mobile.
- Use 8 px between tightly related controls.
- Use 12 px between label/helper/control groups.
- Use 32 px between major page regions.
- Use 48 px minimum vertical breathing room for empty states.

## 6. Grid and layout

### Desktop grid

- Use a **12-column responsive content grid** for dashboard, knowledge, settings, and future admin pages.
- Use **application shell zones** for Chat:
  - Global sidebar: 72 px collapsed or 240 px expanded.
  - Chat session sidebar: 280-336 px.
  - Main chat canvas: fluid, max readable width for messages.
  - Context panel: 320-400 px when open.
- Use 24 px page gutters on desktop and 16 px on tablet/mobile.

### Layout widths

| Surface | Recommended width |
| --- | --- |
| Chat message column | 720-880 px max readable content width. |
| Composer | Align to message column; can expand to 960 px. |
| Modal medium | 520-640 px. |
| Modal large | 720-960 px. |
| Command palette | 640-760 px desktop, full-screen mobile. |
| Settings form | 640-760 px content width. |
| Status card grid | 3 columns desktop, 2 tablet, 1 mobile. |

### Grid rules

- Chat should not use a rigid 12-column grid inside the message timeline; optimize for reading.
- Operational pages use cards aligned to the 12-column grid.
- Context panels align to shell boundaries, not the content grid.
- Avoid centered narrow layouts for dense operator/status data.
- Preserve stable layout during loading by matching skeleton dimensions to final components.

## 7. Corner radius

### Radius scale

| Token | Value | Usage |
| --- | --- | --- |
| `radius/none` | 0 | Tables, dividers, flush shell edges. |
| `radius/xs` | 4 | Badges, code inline, tiny controls. |
| `radius/sm` | 6 | Inputs, menu items, compact buttons. |
| `radius/md` | 8 | Default buttons, tabs, alerts. |
| `radius/lg` | 12 | Cards, chat bubbles, dropdowns. |
| `radius/xl` | 16 | Modals, large panels, command palette. |
| `radius/2xl` | 24 | Empty state visual containers, onboarding panels. |
| `radius/full` | 999 | Pills, avatars, status dots. |

### Radius rules

- Use 12 px for most cards and chat bubbles.
- Use 8 px for controls so the interface feels precise rather than bubbly.
- Use 16 px for large overlays to create a premium softened feel.
- Avoid mixing more than two radius sizes in a single component.
- Nested elements should generally have a smaller radius than their parent.

## 8. Elevation and shadows

### Elevation model

Doitall uses subtle elevation. Prefer borders plus soft shadows instead of heavy drop shadows.

| Token | Light mode shadow | Dark mode shadow | Usage |
| --- | --- | --- | --- |
| `elevation/0` | none | none | Flat surfaces, table rows. |
| `elevation/1` | `0 1px 2px rgba(15,23,42,.06)` | `0 1px 0 rgba(255,255,255,.04)` | Cards and controls. |
| `elevation/2` | `0 8px 24px rgba(15,23,42,.08)` | `0 12px 32px rgba(0,0,0,.35)` | Dropdowns, popovers. |
| `elevation/3` | `0 16px 48px rgba(15,23,42,.12)` | `0 20px 60px rgba(0,0,0,.50)` | Modals and command palette. |
| `elevation/glow` | `0 0 0 1px rgba(99,91,255,.15), 0 16px 56px rgba(99,91,255,.16)` | `0 0 0 1px rgba(167,155,255,.22), 0 20px 70px rgba(99,91,255,.24)` | Focused AI panels, onboarding hero, command palette. |

### Elevation rules

- Use borders for normal hierarchy; reserve shadows for overlays and active floating surfaces.
- Dark mode elevation relies more on tonal surface changes and subtle outer shadows.
- Do not place multiple glowing surfaces next to each other.
- Active streaming can use a faint aurora edge or glow, but avoid pulsing large panels.

## 9. Icons

### Icon style

- Use a single outline icon family with consistent stroke weight, preferably 1.75 px or 2 px.
- Icons should be geometric but slightly rounded to match the radius system.
- Use filled icons only for selected states or critical status markers if needed.
- Avoid decorative AI sparkle overuse; the product should feel intelligent, not gimmicky.

### Icon sizes

| Token | Size | Usage |
| --- | --- | --- |
| `icon/xs` | 12 | Badges, metadata. |
| `icon/sm` | 16 | Buttons, inputs, menu items. |
| `icon/md` | 20 | Navigation, cards, alerts. |
| `icon/lg` | 24 | Empty states, section headers. |
| `icon/xl` | 32 | Hero/onboarding illustrations only. |

### Icon rules

- Pair icons with labels for primary navigation.
- Icon-only actions require accessible labels and tooltips.
- Status icons must be paired with status text.
- Use consistent metaphors:
  - Chat: message bubble or conversation lines.
  - Knowledge: layered document or database page.
  - Dashboard: pulse or status grid.
  - Memory: node or bookmark-like memory mark.
  - Tools & Skills: connected nodes or tool glyph.
  - Settings: sliders, not gear-heavy visual clutter.

## 10. Animations and motion

### Motion personality

Motion should communicate responsiveness and state change. It should feel fast, precise, and calm.

### Motion tokens

| Token | Duration | Usage |
| --- | --- | --- |
| `motion/instant` | 80 ms | Press states, tiny icon transitions. |
| `motion/fast` | 120 ms | Button hover, focus, menu item highlight. |
| `motion/base` | 180 ms | Dropdowns, drawers, toast entry. |
| `motion/slow` | 260 ms | Modals, command palette, page panels. |
| `motion/ambient` | 1200-2400 ms | Optional subtle aurora shimmer or streaming indicator. |

### Easing tokens

| Token | Curve | Usage |
| --- | --- | --- |
| `ease/standard` | `cubic-bezier(.2, 0, 0, 1)` | Default UI movement. |
| `ease/enter` | `cubic-bezier(.16, 1, .3, 1)` | Overlay entry, panels. |
| `ease/exit` | `cubic-bezier(.7, 0, .84, 0)` | Overlay exit. |
| `ease/spring-soft` | Design note only | Very subtle micro-interactions; avoid bouncy UI. |

### Animation rules

- Animate opacity and transform, not layout-heavy properties, where possible.
- Keep hover transitions under 150 ms.
- Keep overlay transitions under 260 ms.
- Avoid constant motion in the chat timeline.
- Respect `prefers-reduced-motion`; replace motion with instant state changes and static indicators.

## 11. Micro animations

### Recommended micro animations

| Pattern | Motion | Purpose |
| --- | --- | --- |
| Button press | 1 px vertical compression or 98% scale for 80 ms | Confirms activation without feeling playful. |
| Focus ring | 120 ms fade/outline expansion | Helps keyboard users track focus. |
| Streaming cursor | Subtle opacity pulse on caret/dot | Shows AI response is active. |
| New message entry | 8 px upward translate + fade in over 180 ms | Adds continuity without distracting. |
| Toast entry | Slide/fade from edge over 180 ms | Confirms secondary outcomes. |
| Command palette open | Scale from 98% to 100% + fade over 180 ms | Feels premium and fast. |
| Provider status refresh | Dot rotates or swaps state over 120 ms | Shows status was rechecked. |
| Copy success | Icon morph/check fade for 900 ms | Confirms copy action. |

### Micro animation rules

- Never animate every streamed token individually.
- Avoid confetti, bouncing, or exaggerated easing.
- Use motion to clarify causality: action → state change → outcome.
- Keep destructive action animations restrained and clear.

## 12. Interaction patterns

### Global interactions

- **Command-first navigation:** `Cmd/Ctrl+K` opens the command palette. The visual treatment should feel like a premium control surface with high contrast, strong focus, and grouped results.
- **Status as a doorway:** Clicking global readiness or provider status opens Dashboard/Status or a popover with clear impact and remediation.
- **Contextual over global destructive actions:** Delete, clear, and future admin actions appear near the object and require confirmation.
- **Progressive disclosure:** Advanced diagnostics, metadata, schemas, and future debug details live in accordions or context panels.

### Chat interactions

- Composer is the primary interaction anchor.
- Enter/Shift+Enter behavior must be visible in helper text or shortcut hint.
- Provider selection should be visible before send but not dominate the composer.
- Streaming state appears inline with the assistant response and as subtle composer status.
- Retry appears where the failure happened, not only in a toast.

### Form interactions

- Validate obvious empty/format errors before submission.
- Preserve drafts on recoverable errors.
- Place form-level errors above the submit action and field errors next to fields.
- Disable duplicate submit while preserving explanatory loading text.

### Navigation interactions

- Route changes move focus to the page heading.
- Active route and active session are visually and programmatically distinct.
- Mobile drawers close after navigation and return focus predictably.

## 13. Component spacing

### Control spacing

| Component | Internal padding | Gap | Notes |
| --- | --- | --- | --- |
| Button `md` | 10 px vertical, 14 px horizontal | 8 px icon gap | Height 40 px. |
| IconButton `md` | 10 px | n/a | Hit area 40 px desktop, 44 px touch. |
| Input `md` | 10 px vertical, 12 px horizontal | 8 px adornment gap | Height 40 px. |
| Textarea | 12 px vertical, 14 px horizontal | n/a | Composer min height 52 px. |
| Badge | 3 px vertical, 8 px horizontal | 4 px icon gap | Pill or small radius. |
| Menu item | 8 px vertical, 10 px horizontal | 10 px icon gap | Minimum 36 px high. |
| Tab | 8 px vertical, 12 px horizontal | 8 px icon gap | 40 px min target. |

### Layout spacing

| Component | Desktop | Mobile | Notes |
| --- | --- | --- | --- |
| Card padding | 20-24 px | 16 px | Use 20 px for dense cards. |
| Modal padding | 24-32 px | 20 px | Full-screen mobile keeps 20 px. |
| Sidebar item gap | 4-8 px | 6-8 px | Keep navigation scannable. |
| Chat bubble padding | 14-18 px | 12-14 px | Assistant markdown can use more line height. |
| Message gap | 20-28 px | 16-20 px | Streaming pending state may be tighter. |
| Form field gap | 16-20 px | 16 px | Label/helper inside field group. |
| Page section gap | 32-40 px | 24-32 px | Empty states may use more. |

## 14. Loading states

### Loading principles

- Loading should reassure users that the system is working.
- Use skeletons when layout is known and spinners only for small inline operations.
- Streaming should have its own distinct state, not a generic spinner.
- Loading states must preserve user drafts and avoid layout jumps.

### Loading patterns

| Surface | Pattern | Notes |
| --- | --- | --- |
| App boot | Shell skeleton + status check message | Show setup screen only after connection failure is known. |
| Session list | Sidebar row skeletons | Match row height and metadata lines. |
| Session detail | Message skeletons | Use user/assistant bubble skeleton variation. |
| Provider list | Card skeletons or inline status dots | Avoid aggressive polling. |
| Knowledge ingestion | Button loading + progress text | Future ingestion jobs can use progress bar. |
| Command palette | Inline result skeletons | Keep search input focused. |
| Dashboard | Card skeletons | Show last-known status if available and mark stale. |

### Skeleton style

- Light mode: base `#E2E8F0`, highlight `#F8FAFC`.
- Dark mode: base `#1C2430`, highlight `#2A3444`.
- Animation: slow shimmer only if reduced motion is not requested; otherwise static blocks.
- Radius should match final component.

## 15. Empty states

### Empty state tone

Empty states should be helpful, not cute. They should explain what can be done now and what may require setup.

### Empty state structure

1. Small visual mark or icon.
2. Clear title.
3. One-sentence explanation.
4. Primary action.
5. Optional secondary actions.
6. Optional setup or limitation note.

### Empty state examples

| State | Title direction | Primary action | Secondary action |
| --- | --- | --- | --- |
| No sessions | “Start your first conversation” | Start a chat | Ingest knowledge, view status. |
| Empty active chat | “Ask Doitall anything about your workspace” | Composer focus | Try example prompt. |
| No providers | “No providers are available” | Open status | Configure API/provider. |
| No commands | “No commands found” | Clear search | Continue typing. |
| No knowledge list | “Text ingestion is ready” | Ingest text | Explain document management is future. |
| No memories | “Memory controls are not enabled yet” | Return to Chat | Learn what is required. |
| No search results | “No matching results” | Clear search | Change scope. |

### Empty state visual rules

- Use simple abstract aurora-line illustrations or icons, not mascots.
- Keep visual marks subtle and consistent.
- Avoid implying future capabilities are already available.
- Place empty states within the relevant container, not always full page.

## 16. Error states

### Error principles

- Errors should be plain-language, specific, and recoverable when possible.
- Technical details should be available to developers without overwhelming end users.
- Error visuals should distinguish auth, rate limit, provider, stream, validation, backend, and not-found failures.

### Error state taxonomy

| Error | Visual treatment | Action |
| --- | --- | --- |
| Unauthorized | Warning/danger alert with key icon | Enter API key, clear key, retry. |
| Rate limited | Warning alert with countdown if available | Wait and retry. |
| Provider unavailable | Warning status with provider icon | Switch provider, view status. |
| Stream failure | Inline failed assistant bubble | Retry, switch provider. |
| Validation failure | Field-level error + form summary | Fix fields. |
| Backend unavailable | Full setup/error screen or banner | Edit API URL, retry. |
| Readiness degraded | Persistent warning banner | View Dashboard, refresh. |
| Not found | Route-level error page | Start new chat, return to list. |
| Destructive failure | Inline alert near action | Retry, keep object visible. |

### Error visual rules

- Use danger red for failed/destructive states, warning amber for degraded/recoverable setup states.
- Pair status with icon and text.
- Include request ID/session ID copy affordance when available.
- Keep retry actions close to the failed context.
- Never hide critical errors in transient toasts only.

## 17. Light mode

### Light mode personality

Light mode should feel crisp, calm, and editorial. It should support long reading sessions without feeling sterile.

### Light mode rules

- Page background uses very light graphite, not pure white, to allow cards and chat panels to layer.
- Primary surfaces are white with subtle borders.
- Chat user bubbles can use a soft aurora-tinted fill; assistant bubbles should often remain surface-neutral for readability.
- Code blocks use a slightly cool tinted background with clear border.
- Shadows remain extremely soft; borders provide most structure.
- Active navigation uses aurora accent with a subtle tinted background, not a saturated block.

## 18. Dark mode

### Dark mode personality

Dark mode should feel like a premium command center: deep, quiet, and high-contrast enough for long technical work.

### Dark mode rules

- Avoid pure black for cards; use layered graphite surfaces.
- Use aurora accents more luminously but less frequently.
- Borders should be visible but subtle; use `neutral/200` dark token for normal borders and `neutral/300` for active outlines.
- Chat assistant content must remain high contrast and comfortable to read.
- Code blocks can be slightly darker than panels with syntax colors tuned for accessibility.
- Glows should be faint and localized to focused AI/command surfaces.
- Disabled states must remain readable, not disappear into the background.

## 19. Accessibility

### Contrast

- Body text must meet WCAG AA contrast: 4.5:1 minimum.
- Large text and icon-only controls should meet 3:1 minimum.
- Focus rings must meet 3:1 against adjacent colors.
- Status colors require text labels and should pass contrast in both modes.

### Keyboard and focus

- Every action must be keyboard reachable.
- Focus outlines should be visible, rounded to match component radius, and offset by 2 px when possible.
- Overlay focus should be trapped only for modal surfaces.
- Closing overlays returns focus to the trigger.
- Route changes move focus to the page heading or first meaningful region.

### Motion accessibility

- Respect reduced-motion preference.
- Disable shimmer, pulsing glows, and slide animations in reduced motion.
- Do not animate large content shifts.
- Avoid rapid blinking or flashing.

### Content accessibility

- Do not rely on placeholder text as labels.
- Use clear labels for icon-only buttons.
- Use readable timestamps and exact values in tooltips or detail panels.
- Markdown rendering must preserve semantic headings, lists, links, code blocks, and tables.
- Live regions for streaming should announce state changes, not every token.

## 20. Responsive rules

### Breakpoints

| Token | Width | Usage |
| --- | --- | --- |
| `breakpoint/mobile` | < 640 px | Single-column, drawers/bottom sheets, sticky composer. |
| `breakpoint/tablet` | 640-1023 px | Collapsed shell, optional context drawer. |
| `breakpoint/desktop` | 1024-1439 px | Full shell with sidebars and main content. |
| `breakpoint/wide` | >= 1440 px | Optional context panel and wider operational grids. |

### Responsive behavior

- Global sidebar becomes drawer or bottom navigation on mobile.
- Chat session sidebar becomes a drawer on tablet/mobile.
- Context panels become bottom sheets or route-level panels on mobile.
- Top nav actions collapse into overflow; critical status remains visible.
- Composer stays sticky at bottom with safe-area padding.
- Tables become responsive cards or horizontally scroll only when content remains comprehensible.
- Cards stack to one column on mobile.
- Modals become full-screen when content requires forms or search.

## 21. Component-specific visual guidance

### Buttons

- Primary button: aurora fill, white text, soft hover darkening/lightening.
- Secondary button: neutral surface, strong border, primary text.
- Ghost button: transparent, hover surface fill.
- Danger button: danger fill only for confirmed destructive contexts; otherwise outline danger.
- Loading button: preserve width and show label such as “Sending…” or “Ingesting…”.

### Inputs

- Default height 40 px.
- Use clear labels and helper text.
- Focus ring uses aurora token and subtle border intensification.
- Invalid state uses danger border plus field message.
- Secret/API-key inputs support reveal/hide and clear.

### Cards

- Cards use 12 px radius, subtle border, and elevation 1 by default.
- Interactive cards add hover border and slight lift only when they are genuinely clickable.
- Status cards use left accent strip or header badge, not full saturated backgrounds.

### Tables

- Table headers are compact, muted, and semibold.
- Rows use subtle hover fill and visible focus for keyboard navigation.
- Row actions appear on hover/focus but remain accessible by keyboard.
- Empty table state appears inside table frame.

### Chat bubbles

- Assistant messages prioritize long-form readability and may be neutral surface without a heavy bubble.
- User messages can use a soft aurora-tinted bubble aligned to the user side on desktop.
- Error bubbles use inline alert treatment.
- Tool-result-safe bubbles use compact technical styling with clear tool label.

### Code blocks

- Use mono type, 13 px size, 20 px line height.
- Header contains language/file label and copy action.
- Use accessible syntax highlighting in both modes.
- Long code blocks support max height with expand.

### Markdown renderer

- Paragraph rhythm: 12-16 px between paragraphs.
- Lists align cleanly and preserve indentation.
- Tables scroll horizontally inside the message container.
- Links use visible underline or underline on hover/focus plus accessible contrast.

### Sidebars

- Global sidebar uses stronger navigation hierarchy.
- Chat sidebar uses compact session rows with active selection background.
- Sidebar dividers are subtle; avoid heavy rails.
- Collapsed sidebar keeps tooltips and accessible labels.

### Dialogs, modals, and dropdowns

- Overlays use elevation 2-3 and radius xl.
- Backdrop should be subtle blur/tint, not opaque black except critical modals.
- Dropdowns use 8 px item radius and 4 px internal menu padding.
- Modal actions align right on desktop and stack on mobile when needed.

### Toasts and alerts

- Toasts appear away from the composer on mobile.
- Alerts remain in context and should not auto-dismiss if critical.
- Use tone icon, title, description, and action layout consistently.

### Tabs and accordions

- Tabs use underline or pill treatment depending on density.
- Active tab uses aurora accent and strong text.
- Accordions use chevron rotation and clear focus ring.
- Accordion content should not hide critical errors by default.

### Tool, memory, and agent cards

- These cards should feel capability-driven and transparent.
- Show status, permissions, scope, and capability state as text badges.
- Use subdued technical metadata and avoid exposing sensitive paths or private content.
- Future/admin actions use clear disabled states until authorization exists.

## 22. Figma component spacing annotations

Every component frame in Figma should include annotations for:

- Internal padding.
- Gap between icon and label.
- Minimum touch target.
- Desktop/tablet/mobile behavior.
- Focus ring bounds.
- Loading/disabled/error states.
- Token references for color, type, radius, and shadow.

### Auto layout rules

- Use auto layout for all components.
- Avoid absolute positioning except for decorative background glows.
- Use min/max width constraints for cards, modals, and sidebars.
- Use component properties for icon on/off, loading on/off, tone, size, and state.
- Use variants for semantic state and mode, not one-off duplicated frames.

## 23. Design QA checklist

Before a Figma screen is considered ready for implementation, verify:

- The screen uses the correct light and dark mode variables.
- Text styles map to named tokens.
- Spacing uses the 4 px scale.
- Components use documented radius and elevation tokens.
- All interactive controls have focus states.
- Loading, empty, error, disabled, hover, active, and selected states are designed where relevant.
- Status is communicated with text and icon, not color alone.
- Mobile and tablet behavior are defined.
- Reduced-motion alternatives are noted for any continuous animation.
- Markdown/code content is shown in realistic long-content examples.
- Sensitive/API-key/tool-output areas include security-conscious copy and redaction patterns.

## 24. Summary

Doitall's visual language should feel premium through restraint, precision, and trust rather than ornament. The system uses graphite surfaces, aurora accents, strong typography, careful spacing, subtle depth, accessible status language, and calm motion to create an original AI platform experience. In Figma, these guidelines should become variables, components, variants, and prototypes that help the product move from MVP chat workspace to a broader agent operations platform without losing coherence.
