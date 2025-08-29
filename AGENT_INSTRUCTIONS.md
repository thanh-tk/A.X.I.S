# AXIS Agent Instructions

**File:** `AGENT_INSTRUCTIONS.md`

> Contract and operating guide for the AXIS Agent that drives cockpit control, integrates perception/decision/control, and exposes a stable API for skills.

---

## 0) Scope

* Audience: core contributors, skill authors.
* Coverage: lifecycle, interfaces, safety, performance, configurability, testing, and versioning.
* Out of scope: full README (lives in `README.md`), marketing, installation screenshots.

---

## 1) Roles & Responsibilities

* **Agent Core**: maintains the Perception→Decision→Control (PDC) loop; arbitrates skills; enforces safety.
* **Perception**: supplies `CockpitState` from pixels + Journal; provides confidence/staleness per field.
* **Decision**: hierarchical finite-state machine (HFSM) + behavior trees to achieve goals.
* **Control**: emits human-like HID inputs only (keyboard/mouse/joystick). No memory/process injection.
* **Skills Runtime**: sandbox for user routines with a small, permissioned API.

---

## 2) Lifecycle

1. **Boot**

   * Load config, schemas, and skill manifests.
   * Bind global panic hotkey and start watchdog.
2. **Capability Discovery**

   * Detect displays, window bounds, fps; read keybind export; enumerate HID outputs.
3. **Pipelines Start**

   * Perception loop (frame capture → detect → OCR → fuse → `CockpitState`).
   * Journal stream (subscribe to file changes).
   * Event Bus online (typed pub/sub).
4. **Decision Loop**

   * HFSM tick at ≥ 30 Hz; behavior-tree nodes run actions with pre/post conditions.
5. **Skill Attach**

   * Start per-skill processes; verify permissions; subscribe to events.
6. **Steady State**

   * Maintain latency targets; adjust risk parameters with telemetry.
7. **Shutdown**

   * Zero throttle, cancel boost; disable HID; flush logs.

---

## 3) Event Bus Contract

**Envelope**

```json
{
  "type": "string",            // e.g., "perception.cockpit_state", "action.request", "skill.log"
  "ts": 1690000000.123,         // unix seconds with ms
  "v": "1.0.0",                // schema version
  "trace": "uuid-...",          // correlation id
  "payload": { }
}
```

**Topics (non-exhaustive)**

* `perception.cockpit_state`
* `journal.event`
* `decision.state_entered` / `decision.state_exited`
* `action.request` / `action.progress` / `action.result`
* `safety.alert` (overheat, low confidence, heartbeat gap)
* `skill.event` / `skill.error`

---

## 4) Perception → `CockpitState`

**Payload**

```json
{
  "screen": {"w":1920, "h":1080},
  "markers": [
    {"k":"target", "cx":965, "cy":545, "conf":0.92, "age_ms":12},
    {"k":"pad_number", "bbox":[880,720,940,760], "text":"36", "conf":0.88, "age_ms":20}
  ],
  "gauges": {
    "heat": {"val":0.63, "conf":0.97, "age_ms":8},
    "fuel": {"val":0.82, "conf":0.99, "age_ms":8},
    "speed": {"val":191, "conf":0.95, "age_ms":8}
  },
  "quality": {"fps":120, "latency_ms":14}
}
```

**Rules**

* Every numeric field carries `conf` ∈ \[0,1] and `age_ms` to support time-aware decisions.
* Low confidence or stale fields must not drive control without fallbacks.

---

## 5) Control API (Agent-internal)

**Motion primitives** (time- and rate-safe)

* `yaw(rate: -1..1, duration_ms)`
* `pitch(rate: -1..1, duration_ms)`
* `roll(rate: -1..1, duration_ms)`
* `throttle(percent: 0..1)`
* `boost()`
* `brake_to(stop_condition)`
* `gear(deployed: bool)`
* `lights(on: bool)`
* `ui_nav(path: string[])`  // navigates panels/menus

**High-level actions** (compose primitives)

* `align_to(marker, tolerance_px)`
* `enter_supercruise()` / `exit_supercruise()`
* `plot_next_system()` / `jump_next_in_route()`
* `request_docking()` / `dock_to(pad_id | "auto")`
* `scoop_until(level: 0..1)`

**Contract**

* Each action declares: **preconditions**, **postconditions**, **timeout_ms**, **abort_on** events, and **fallbacks**.
* Outputs are **rate-limited** and **jittered** (±5%) to mimic human variability.
* Manual input detection suspends control until explicitly resumed.

---

## 6) Decision Layer

* **HFSM** with named states and guarded transitions; re-entry allowed.
* **Behavior Trees** for sequencing and fallback (selector/sequencer/retry with backoff).
* **Pipelines**

  * Docking: `Approach → SlotAlign → InteriorAlign → PadAcquire → FinalDescent → Touchdown`.
  * Jumping: `TargetAcquire → AlignToVector → Spool → ChargeGuard → Hyperspace → Cooldown`.
* **Risk Engine**: widens tolerances and slows control under low fps/high latency; yields to manual control on conflict.

---

## 7) Skills Runtime

**Manifest**

```json
{
  "name": "AutoHaul",
  "version": "0.1.0",
  "triggers": ["Docked", "CargoDepotCollect"],
  "permissions": ["navigation", "cargo", "ui"],
  "requires": ["perception.target", "gauges.fuel", "action.jump_next_in_route"]
}
```

**Skill API**

* `on(event: string, handler)`
* `await(predicate: CockpitState -> bool, timeout_ms)`
* `do(action: string, params)`

**Isolation & Limits**

* Per-skill process; CPU/RAM caps; permissioned IPC; hot-reload.
* Static checks: no filesystem writes outside `~/.axis`; no network unless declared.

---

## 8) Safety & Compliance

* **Panic toggle**: immediate HID disable + state freeze.
* **Watchdog**: triggers on heartbeat gaps (>250 ms), perception confidence drops, or unbounded action duration.
* **Fail-safe defaults**: throttle 0, cancel boost, neutral attitude.
* **EULA posture**: pixels in, HID out; no DLL injection, no memory editing.

---

## 9) Performance Targets

* PDC end-to-end ≤ 50 ms typical at 60 fps; ≤ 30 ms target on capable hardware.
* Detector ≤ 12 ms; OCR ≤ 5 ms; fusion ≤ 3 ms; control emission ≤ 10 ms.
* Input smoothing window 16–32 ms with bounded latency contribution.

---

## 10) Configuration

**File:** `axis.config.yaml`

```yaml
video:
  monitor: 1
  target_fps: 120
  normalize: 1920x1080
control:
  device: vjoy0
  jitter: 0.05   # ±5%
  rate_limit_ms: 16
safety:
  heartbeat_ms: 250
  conf_min: 0.75
skills:
  allow_network: false
  paths:
    - ./skills
logging:
  level: info
  record_video: false
```

---

## 11) Observability & Telemetry

* Web dashboard panels: **State**, **Confidence**, **Route**, **Heat/Fuel**, **Latency**, **Alarms**.
* Each action publishes `action.progress` updates (0–100%).
* Tracing: propagate `trace` id across perception→decision→control.

---

## 12) Testing & Validation

* **Unit**: geometry/PID/timers.
* **Perception regression**: mAP for detectors; OCR exact-match per HUD theme.
* **Scenario**: journal replays + recorded video; assert event timelines and safety triggers.
* **Soak**: 3-hour travel with jitter; watchdog must not trip; no control runaway.
* **Acceptance** (examples)

  * Reticle hold within ±3% for 30 s.
  * 10 consecutive jumps; max heat ≤ 75%.
  * 9/10 docks from 7 km approach; zero collisions in test set.

---

## 13) Failure Modes & Recovery

* **Low confidence/stale state** → suspend control; re-acquire detections; notify.
* **Input conflict** → pause on manual input; resume on explicit command.
* **Planner dead-end** → backtrack to safe state; replot or await pilot.

---

## 14) Versioning & Compatibility

* Semantic versioning for schemas and APIs.
* `v` field in envelopes must match major version; minor features are additive.
* Skills declare minimum agent version; agent refuses incompatible skills.

---

## 15) Contributor Checklist

* Respect human-like IO contract.
* Add/update JSON Schemas when touching message formats.
* Include new test clips & fixtures for perception changes.
* Document every new action: pre/post, timeouts, aborts, fallbacks.

---

## 16) Quick Start for Agent Developers

* Configure `axis.config.yaml`.
* Launch `axis dev run` (hot-reload + overlay + bus inspector).
* Verify dashboard metrics (fps, latency, confidence).
* Implement or extend actions; add tests; open PR.

> This file defines how the Agent behaves and interfaces within AXIS. Treat it as the authoritative contract for cockpit control and skill integration.

