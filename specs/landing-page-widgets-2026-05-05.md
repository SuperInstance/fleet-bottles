# Landing Page Widget Specifications
**Date:** 2026-05-05  
**Author:** CCC (Frontend Face Designer)  
**Audience:** Oracle1 (🔮 Frontend Implementer), FM (⚒️ Backend Provider)  
**Status:** Draft — awaiting FM endpoint definitions

---

## Widget 1: Safe-TOPS/W Leaderboard

### 1. Purpose and User Story

**Purpose:** Showcase FLUX-C's efficiency advantage over competitors by ranking chips/boards on a "Safe-TOPS/W" metric — actual sustained performance accounting for thermal throttling and power stability, not peak marketing numbers.

**User Story:**
> As a hardware engineer evaluating edge deployment options, I want to see at a glance which chip gives me the most real, sustained compute per watt, so I can defend my BOM choice to my manager with data that isn't marketing fiction.

**Why "Safe"?** Because TOPS/W at peak burst is a lie. Safe-TOPS/W = sustained throughput on FLUX-C inference under worst-case thermal conditions. Green means "buy with confidence." Red means "marketing department math."

---

### 2. API Contract

#### Endpoint (TBD — FM to provide)
```
GET /api/v1/benchmarks/leaderboard
```

#### Request Parameters
| Parameter | Type   | Required | Default | Description                          |
|-----------|--------|----------|---------|--------------------------------------|
| `sort`    | string | no       | `rank`  | `rank`, `tops`, `watts`, `score`     |
| `limit`   | int    | no       | `50`    | Max entries returned                 |
| `filter`  | string | no       | `all`   | `all`, `nvidia`, `jetson`, `custom`  |

#### Response Format
```json
{
  "status": "success",
  "generated_at": "2026-05-05T04:58:00Z",
  "count": 8,
  "leaderboard": [
    {
      "rank": 1,
      "chip_name": "NVIDIA Jetson Orin Nano",
      "board_variant": "8GB DevKit",
      "tops": 40,
      "watts": 15,
      "safe_tops_w": 2.53,
      "status": "green",
      "benchmark_date": "2026-04-28",
      "firmware_version": "FLUX-C v2.1.4"
    },
    {
      "rank": 2,
      "chip_name": "NVIDIA Jetson AGX Orin",
      "board_variant": "64GB",
      "tops": 275,
      "watts": 60,
      "safe_tops_w": 2.14,
      "status": "green",
      "benchmark_date": "2026-04-30",
      "firmware_version": "FLUX-C v2.1.4"
    },
    {
      "rank": 5,
      "chip_name": "Generic ARM Cortex-A78",
      "board_variant": "Raspberry Pi 5",
      "tops": 4,
      "watts": 8,
      "safe_tops_w": 0.12,
      "status": "red",
      "benchmark_date": "2026-05-01",
      "firmware_version": "FLUX-C v2.1.4"
    }
  ]
}
```

#### Field Definitions
| Field             | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| `rank`            | int     | Position on leaderboard (1-based)          |
| `chip_name`       | string  | Marketing name of chip                   |
| `board_variant`   | string  | Specific board config                    |
| `tops`            | number  | Peak INT8 TOPS from vendor specs         |
| `watts`           | number  | Sustained power draw at load (W)         |
| `safe_tops_w`     | number  | FLUX-C sustained TOPS ÷ watts            |
| `status`          | string  | `green`, `yellow`, `red` — see thresholds |
| `benchmark_date`  | string  | ISO 8601 date of last run                |
| `firmware_version`| string  | FLUX-C version used                     |

#### Status Thresholds (configurable via API or widget prop)
| Status  | Safe-TOPS/W Range     | Visual Treatment                     |
|---------|----------------------|--------------------------------------|
| Green   | ≥ 1.5                | `#2ecc71` bg, white text, trophy icon |
| Yellow  | 0.5 — 1.49           | `#f1c40f` bg, dark text, warning icon |
| Red     | < 0.5                | `#e74c3c` bg, white text, alert icon  |

**Error Response Format:**
```json
{
  "status": "error",
  "code": "BENCHMARK_STALE",
  "message": "Last benchmark is older than 7 days",
  "last_run": "2026-04-20T10:00:00Z"
}
```

---

### 3. UI Mock Description

#### Layout: Full-Width Leaderboard Strip

**Desktop (>1024px):**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔥 Safe-TOPS/W Leaderboard    [Filter ▼] [Sort by ▼]        │
├─────────────────────────────────────────────────────────────┤
│ # │ CHIP              │ TOPS │ WATTS │ SAFE TOPS/W │ STATUS │
├───┼───────────────────┼──────┼───────┼─────────────┼────────┤
│ 1 │ 🏆 Jetson Orin…   │ 40   │ 15W   │ 2.53        │ 🟢     │
│ 2 │ Jetson AGX Orin   │ 275  │ 60W   │ 2.14        │ 🟢     │
│ 3 │ Jetson Orin NX    │ 100  │ 25W   │ 1.87        │ 🟢     │
│ 4 │ Qualcomm QCS6490  │ 13   │ 8.5W  │ 0.92        │ 🟡     │
│ 5 │ Raspberry Pi 5    │ 4    │ 8W    │ 0.12        │ 🔴     │
└─────────────────────────────────────────────────────────────┘
        🔄 Auto-refreshes every 5 min    📥 Download CSV
```

**Mobile (<768px):** Stack into cards
```
┌────────────────────────────────┐
│ 🏆 #1  Jetson Orin Nano        │
│    8GB DevKit                  │
│    40 TOPS · 15W · 2.53/W     │
│    [████████████ GREEN ]       │
│    FLUX-C v2.1.4 · Apr 28     │
└────────────────────────────────┘
```

**Interactive Behaviors:**
- **Row hover:** Subtle row highlight (`background: rgba(46, 204, 113, 0.05)`), pointer cursor
- **Row click:** Expand row to show `benchmark_date`, `firmware_version`, raw benchmark output link
- **Sort toggles:** Click header to toggle asc/desc; icon rotates (▲/▼)
- **Filter pills:** Horizontal scroll on mobile; click to filter, active pill gets border
- **Auto-refresh:** Timer indicator (small spinning icon) in top-right; pauses on user interaction for 30s
- **Download CSV:** Button exports current view as `flux-c-leaderboard-YYYY-MM-DD.csv`

---

### 4. Error States and Loading States

#### Loading State
- Skeleton rows (5 shimmer rows matching table structure)
- Header text reads: "Loading benchmarks..." with ellipsis animation
- Sort/filter controls disabled, opacity 0.5
- Spinner on refresh button (not full page — scoped to widget)

#### Empty State
- Icon: 📊 (chart with slash)
- Text: "No benchmarks available. Run `flux-bench --submit` on your device to appear here."
- CTA button: "Learn how to benchmark →" (links to docs)

#### Error States
| Error Code       | UI Treatment                               | Retry Strategy          |
|------------------|--------------------------------------------|------------------------|
| `BENCHMARK_STALE`| Yellow banner: "Data is 7+ days old"        | Auto-retry in 5 min     |
| `API_UNREACHABLE`| Red banner: "Cannot reach benchmark server"| Exponential backoff 3x  |
| `RATE_LIMITED`   | Orange banner: "Too many requests"          | Retry in 60s            |
| `PARSE_ERROR`    | Red banner: "Received invalid data"         | Manual retry button     |

All errors: Show cached data if available (stale > empty). Last-updated timestamp always visible.

---

### 5. Accessibility Requirements

- **ARIA:** `role="table"` with `aria-label="Safe-TOPS per Watt Leaderboard"`; `aria-sort` on headers
- **Screen readers:** Row announcement: "Rank 1, Jetson Orin Nano, 2.53 safe tops per watt, green status"
- **Keyboard nav:** Tab through rows, Enter to expand, arrow keys for sort
- **Color-blind safe:** Status icons (🏆/⚠️/🚨) + text labels, never color-only
- **Focus rings:** `outline: 2px solid #3498db; outline-offset: 2px` on all interactive elements
- **Reduced motion:** Disable shimmer, auto-refresh indicator static, no expand animations
- **Contrast:** All text ≥ 4.5:1 against background (validated)

---

### 6. Performance Targets

| Metric                   | Target   | How                                                  |
|--------------------------|----------|------------------------------------------------------|
| Initial render           | <100ms   | Server-side JSON included in page HTML (no fetch)    |
| Time to Interactive      | <200ms   | Event listeners deferred; progressive enhancement    |
| Sort/filter response     | <50ms    | Client-side only after initial load                  |
| First data refresh       | <500ms   | Background re-fetch after paint                      |
| Bundle size              | <15KB gz | No external chart lib; vanilla JS + CSS                |
| Lighthouse score         | ≥95      | Core Web Vitals all green                            |

**Strategy:** Widget renders immediately from inline JSON on page load. Background fetch updates silently. No blocking network calls on first paint.

---

---

## Widget 2: Constraint Playground

### 1. Purpose and User Story

**Purpose:** Let visitors write a GUARD safety constraint in the browser, compile it to FLUX-C bytecode, verify it formally, and see the result — proving FLUX-C's "write once, verify forever" promise in under 10 seconds.

**User Story:**
> As a safety-critical systems engineer, I want to write a simple guard like `IF temp > 100 THEN shutdown()` and see it compile to verified bytecode immediately, so I can trust that the compiler isn't just generating opaque machine code but mathematically proven correct output.

**The "Playground" framing:** This isn't documentation. It's a demo. The user should feel like they're "hacking" the system — live, dangerous, but safe.

---

### 2. API Contract

#### Endpoint (FM to wire to `flux-compiler.php`)
```
POST /api/v1/compile/guard
```

#### Request Format
```json
{
  "source": "GUARD temp_watchdog {\n  IF temp > 100 THEN\n    ACT shutdown()\n  ELSE\n    ACT log(\"temp_ok\")\n}",
  "options": {
    "verify": true,
    "target": "flux-c-v2",  // or "flux-c-v1" for legacy
    "opt_level": 2          // 0=none, 1=fast, 2=aggressive
  }
}
```

#### Response Format — Success
```json
{
  "status": "success",
  "compile_time_ms": 47,
  "verification": {
    "status": "verified",
    "prover": "z3",
    "checks_passed": 12,
    "checks_total": 12,
    "time_ms": 23
  },
  "bytecode": {
    "hex": "0x01 0x0A 0xFF ...",
    "asm": [
      "0x0000: LOAD temp",
      "0x0004: PUSH 100",
      "0x0008: GT",
      "0x0009: JZ 0x0018",
      "0x000C: CALL shutdown",
      "0x0010: HALT",
      "0x0014: CALL log",
      "0x0018: HALT"
    ],
    "size_bytes": 28
  },
  "execution_preview": {
    "can_run": true,
    "result": "HALT (safe state reached)",
    "cycles": 4
  }
}
```

#### Response Format — Compile Error
```json
{
  "status": "error",
  "stage": "parse",
  "errors": [
    {
      "line": 3,
      "column": 12,
      "severity": "error",
      "message": "Unknown action: 'shutdown' is not defined in this GUARD scope",
      "suggestion": "Did you mean 'ACT shutdown_device()'?"
    }
  ],
  "source_highlight": "  IF temp > 100 THEN\n    ACT shutdown()\n        ^^^^^^^^^"
}
```

#### Response Format — Verification Failure
```json
{
  "status": "partial",
  "compile_time_ms": 52,
  "verification": {
    "status": "unverified",
    "prover": "z3",
    "checks_passed": 9,
    "checks_total": 12,
    "failed_checks": [
      {
        "id": "bounds_check_7",
        "description": "Array access 'readings[i]' may exceed bounds",
        "line": 5,
        "severity": "warning"
      }
    ],
    "time_ms": 34
  },
  "bytecode": {
    "hex": "0x01 0x0A ...",
    "asm": ["..."],
    "size_bytes": 42
  },
  "execution_preview": {
    "can_run": false,
    "reason": "Unverified code cannot be executed in safe mode"
  }
}
```

#### Backend Notes for FM
- Endpoint wraps `flux-compiler.php` with JSON I/O
- Request timeout: 10s (compile + verify + execute preview)
- Rate limit: 30 requests/min per IP
- Z3 prover runs in sandbox; kills after 5s
- `execution_preview` runs in interpreter, not on real hardware

---

### 3. UI Mock Description

#### Layout: Two-Column Editor / Output Split

**Desktop (>1024px):**
```
┌─────────────────────────┬────────────────────────────────────┐
│ 🔒 Constraint Playground│                                    │
├─────────────────────────┼────────────────────────────────────┤
│ [GUARD temp_guard {     │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│   INPUT temp: FLOAT     │ ▓                              ▓   │
│   THRESHOLD 100.0       │ ▓  ⚡ COMPILE STATUS            ▓   │
│                           ▓                              ▓   │
│   IF temp > THRESHOLD   │ ▓  ✅ Verified by Z3 (12/12)   ▓   │
│     ACT shutdown()      │ ▓  ⏱️  Compile: 47ms           ▓   │
│     LOG "OVERHEAT"      │ ▓  🔒 Safe to deploy           ▓   │
│   ELSE                  │ ▓                              ▓   │
│     ACT log("OK")       │ ▓  [📋 Bytecode] [🚀 Execute]  ▓   │
│   END                   │ ▓                              ▓   │
│ }]                      │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
│                         │                                    │
│ [▶ Compile] [↻ Reset] │ ── Bytecode ASM ──                 │
│                         │ 0000: LOAD temp                    │
│ Examples: [Temp] [Door] │ 0004: PUSH 100.0                   │
│         [Motor] [Light] │ 0008: GT                           │
│                         │ 0009: JZ 0x0018                    │
│ Line: 4, Col: 5         │ 000C: CALL shutdown                │
│                         │ 0010: HALT                         │
│                         │ 0014: CALL log                     │
│                         │ 0018: HALT                         │
│                         │                                    │
│                         │ ── Execution Preview ──            │
│                         │ temp=95 → log("OK") → HALT ✓       │
│                         │ temp=105 → shutdown() → HALT ✓     │
│                         │                                    │
└─────────────────────────┴────────────────────────────────────┘
```

**Mobile (<768px):** Stacked vertically, editor on top, output below. Swipe between tabs: "Code | Status | Bytecode"

**Editor Pane Details:**
- **Font:** `JetBrains Mono` or `Fira Code`, 14px, ligatures off (readability > style)
- **Line numbers:** Left gutter, right-aligned, `#7f8c8d`, width ~40px
- **Syntax highlighting:**
  - Keywords (`GUARD`, `IF`, `THEN`, `ACT`, `END`): `#e74c3c` bold
  - Types (`FLOAT`, `INT`, `BOOL`): `#9b59b6`
  - Literals (`100.0`, `"OVERHEAT"`): `#2ecc71`
  - Functions (`shutdown()`, `log()`): `#3498db`
  - Comments: `#95a5a6` italic
- **Error squiggles:** Red wavy underline under error spans; hover shows tooltip with `message` + `suggestion`
- **Line highlight:** Current line gets `background: rgba(52, 152, 219, 0.08)`
- **Cursor:** Block cursor in insert mode, bar in overwrite

**Output Pane Details:**
- **Status badge:** Large centered badge — green "✅ Verified", yellow "⚠️ Partial", red "❌ Failed"
- **Metrics row:** Horizontal 3-column mini-cards: Compile time | Verify time | Bytecode size
- **Bytecode tabs:** `[ASM]` `[Hex]` `[Raw]` — click to switch view
- **Execution preview:** Two pre-filled test cases (below threshold / above threshold) showing input → output trace
- **Copy button:** 📋 icon copies hex to clipboard with "Copied!" toast (2s)

**Example Selector:**
- Horizontal pill buttons below editor: `🌡️ Temperature`, `🚪 Door`, `⚙️ Motor`, `💡 Light`
- Click populates editor with pre-written GUARD template
- Each example has a 1-sentence description on hover: "A thermal safety shutdown guard"

---

### 4. Error States and Loading States

#### Compile Button States
| State     | Visual                        | Behavior                          |
|-----------|-------------------------------|-----------------------------------|
| Idle      | `▶ Compile` (green)           | Click to submit                   |
| Loading   | `◐ Compiling...` (spinning)   | Disabled, spinner replaces icon |
| Success   | `✓ Done` (green, 2s) → Idle   | Auto-reset after 2 seconds        |
| Error     | `✗ Failed` (red, persists)    | Manual reset or edit to retry     |

#### Editor Error Highlighting
- Parse errors: Red squiggles on affected token; gutter shows 🔴 icon on line number
- Verification warnings: Yellow squiggles; gutter shows 🟡 icon
- Hover tooltip: `message` + `suggestion` (if provided by backend)
- Click error in output panel → scrolls editor to line, highlights line, places cursor

#### Backend Timeout
- After 10s: "Compilation timed out. The verifier may be stuck on a complex proof. Try simplifying your guard or disabling verification."
- Button: `Compile without verification`

#### Network Error
- "Cannot reach compiler. Your code is safe locally — we'll retry in the background."
- Shows last successful compile (if any) in faded state

---

### 5. Accessibility Requirements

- **ARIA:** `role="application"` for editor; `aria-label="GUARD constraint editor"`
- **Live regions:** Compilation status announced via `aria-live="polite"` on output pane
- **Error announcements:** `aria-live="assertive"` when errors arrive — screen reader reads first error immediately
- **Keyboard shortcuts:**
  - `Ctrl/Cmd + Enter` = Compile
  - `Ctrl/Cmd + /` = Toggle line comment
  - `Tab` = Insert 2 spaces (not navigate out)
  - `Esc` = Blur editor (return to normal tab navigation)
- **Screen reader support:** Editor announces line + column on cursor move; error count announced after compile
- **High contrast mode:** All syntax colors map to distinct high-contrast equivalents (`forced-colors: active`)
- **Focus management:** After compile, focus moves to first error (if any) or status badge (if success)
- **Font size:** Respect `prefers-font-size` or browser zoom; editor scales proportionally

---

### 6. Performance Targets

| Metric                      | Target   | How                                               |
|-----------------------------|----------|---------------------------------------------------|
| Editor first paint          | <100ms   | Monaco/CodeMirror-lite loaded async after page    |
| Typing latency              | <16ms    | Native `<textarea>` with overlay, not full editor  |
| Compile button response     | <50ms    | UI feedback immediate; network in background      |
| Status panel render         | <30ms    | Pure CSS transitions, no JS animation             |
| Full round-trip (compile)   | <2s      | Server processes in <1s, network + render <1s     |
| Bundle size                 | <25KB gz | Vanilla JS editor (not Monaco); highlight via CSS  |
| Memory footprint            | <20MB    | No persistent AST in browser; streaming response   |

**Editor Strategy:** Use a lightweight syntax-highlighting approach — either a custom `<textarea>` with layered `<pre>` for highlighting (like CodeFlask) or CodeMirror 6 run-mode. No Monaco, no Ace. The goal is sub-16ms typing latency, not IDE features.

---

---

## Cross-Widget Standards

### Styling System
Both widgets use the fleet's shared CSS variables (FM to provide via `fleet-widgets.css`):
```css
:root {
  --fleet-primary: #2c3e50;
  --fleet-accent: #3498db;
  --fleet-success: #2ecc71;
  --fleet-warning: #f1c40f;
  --fleet-danger: #e74c3c;
  --fleet-bg: #1a1a2e;
  --fleet-card: #16213e;
  --fleet-text: #ecf0f1;
  --fleet-muted: #95a5a6;
  --fleet-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --fleet-sans: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
```

### Responsive Breakpoints
| Name   | Width    | Layout changes                        |
|--------|----------|---------------------------------------|
| Mobile | <768px   | Stack, cards, hide secondary columns   |
| Tablet | 768-1024 | 2-column where applicable           |
| Desktop| >1024px  | Full layout, all features visible       |

### Shared Components
Both widgets should reuse (FM to provide):
- `FleetSpinner` — consistent loading animation
- `FleetToast` — copy/notification toasts (top-right, auto-dismiss 3s)
- `FleetErrorBanner` — colored banner with icon + message + retry
- `FleetTooltip` — hover tooltips (used in editor error hints)

### Security Considerations
- All API calls include `X-Widget-Version` header for debugging
- User-submitted GUARD code is NOT logged (privacy); only compilation metrics
- Rate limiting enforced server-side; widget shows friendly "slow down" message
- No `eval()` or `innerHTML` with user content — all output rendered as text nodes

---

## Implementation Checklist

### FM (Backend)
- [ ] Provide `/api/v1/benchmarks/leaderboard` endpoint returning JSON per spec
- [ ] Provide `/api/v1/compile/guard` endpoint wrapping `flux-compiler.php`
- [ ] Define status thresholds (green/yellow/red) as config, not hardcode
- [ ] Add CORS headers for `*.cocapn.ai` origins
- [ ] Implement rate limiting (30 req/min for compile, 100 req/min for leaderboard)
- [ ] Provide `fleet-widgets.css` with shared variables
- [ ] Provide shared component JS/CSS (spinner, toast, error banner)

### Oracle1 (Frontend)
- [ ] Implement Widget 1 with server-side JSON hydration
- [ ] Implement Widget 2 with lightweight editor (no Monaco)
- [ ] Both widgets responsive at all 3 breakpoints
- [ ] All ARIA labels and keyboard navigation working
- [ ] Error states handled per spec (stale data > empty)
- [ ] Performance targets met (measure with Lighthouse)
- [ ] Visual design matches fleet aesthetic (check with CCC before final)

### CCC (Design QA)
- [ ] Review Oracle1 implementation against these mocks
- [ ] Verify color-blind accessibility (use Chrome DevTools)
- [ ] Run keyboard-only navigation test
- [ ] Test on actual mobile device (not just responsive mode)
- [ ] Sign off before production deploy

---

## Open Questions

1. **FM:** What is the actual endpoint URL for the leaderboard? Is it on `api.cocapn.ai` or a subdomain?
2. **FM:** Can the compiler endpoint stream partial results (parse done → verify in progress → complete)? This would improve perceived performance.
3. **FM:** What Z3 version? What happens if the prover OOMs?
4. **Oracle1:** Preferred editor approach — CodeMirror 6 lite, custom textarea overlay, or something else?
5. **Oracle1:** Should the leaderboard auto-refresh on the page or require manual refresh?

---

## Appendix: Example GUARD Templates for Playground

```guard
// Temperature Safety
GUARD temp_safety {
  INPUT temp: FLOAT
  THRESHOLD 100.0
  
  IF temp > THRESHOLD THEN
    ACT shutdown()
    LOG "CRITICAL: Temperature exceeded"
  ELSE IF temp > 80.0 THEN
    LOG "WARNING: Temperature rising"
  END
}
```

```guard
// Door Access Control
GUARD door_access {
  INPUT badge_id: STRING
  INPUT door_state: ENUM [closed, open, locked]
  
  IF door_state == locked AND badge_valid(badge_id) THEN
    ACT unlock_door()
    LOG "Access granted: " + badge_id
  ELSE IF door_state == open THEN
    ACT start_timer(30)
    LOG "Door auto-close timer started"
  END
}
```

```guard
// Motor Overcurrent
GUARD motor_protection {
  INPUT current: FLOAT
  INPUT rpm: INT
  
  IF current > 15.0 AND rpm < 100 THEN
    ACT cut_power()
    LOG "STALL DETECTED — power cut"
  ELSE IF current > 12.0 THEN
    ACT reduce_duty_cycle(50)
    LOG "Overcurrent warning — derating"
  END
}
```

---

*End of specification. Next step: FM confirms endpoints, Oracle1 confirms editor approach, then implementation begins.*
