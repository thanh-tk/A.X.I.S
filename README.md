# Automated Xenial Intelligence System (AXIS)

## Unified Development Guide (Cockpit‑Control First)

> **Mandate:** AXIS must control the cockpit end‑to‑end (turn, accelerate, stop, dock, jump) while staying robust, extensible, and EULA‑safe.

---

## 1) Purpose & Guardrails

* **Goal:** Automate Elite Dangerous chores (long travel, cargo loops, carrier ops) with player‑programmable routines.
* **Human‑like I/O only:** Read game state via Journal & pixels; write via HID (vJoy + keyboard/mouse) or VoiceAttack. No memory injection.
* **Real‑time PDC loop:** Perception → Decision → Control within ≤ 50 ms typical at 60 fps.
* **Safety:** Global kill switch, watchdog, conservative defaults, idempotent recovery.

---

## 2) Architecture Overview

```
+--------------------+        +----------------------+        +------------------+
|   Perception       |        |  Decision Layer      |        |     Control      |
|  (Vision + OCR)    |  -->   |  (Planner + HFSM)    |  -->   | (HID Actuation)  |
+---------+----------+        +----------+-----------+        +---------+--------+
          ^                              |                               |
          |                              v                               v
     Journal/Telem  <--------------  Typed Event Bus  -------------->  Dashboard
```

**Modules**

1. **Perception:** DXGI capture, HUD parsing, object detection, OCR → `CockpitState`.
2. **Decision:** Hierarchical FSM + behavior trees; goals/tasks; risk engine.
3. **Control:** HID output, motion primitives (rate‑limited, smoothed, jittered).
4. **Skills Runtime:** Sandboxed TS/Python; manifests declare permissions & triggers.
5. **Safety & Observability:** Watchdog, confidence gates, Web UI (fps/latency/heat/fuel/state).

---

## 3) Cockpit Control API

**Motion primitives**

* `yaw(rate, duration)` · `pitch(rate, duration)` · `roll(rate, duration)`
* `throttle(percent)` · `boost()` · `brake_to(stop_condition)`
* `gear(deployed)` · `lights(on)` · `ui_nav(path)`

**High‑level actions**

* `align_to(marker, tolerance)`
* `enter_supercruise()` · `exit_supercruise()`
* `plot_next_system()` · `jump_next_in_route()`
* `request_docking()` · `dock_to(pad_id|"auto")`
* `scoop_until(level)`

**Contract:** Timeouts, fallbacks, aborts; pre/post‑conditions; human‑like jitter & rate limits.

---

## 4) Perception Stack (CV + OCR)

* **Capture:** Desktop Duplication API (DXGI) window‑locked; 120–240 fps target.
* **Detection:** Tiny YOLO for reticle, slot outline, pad chevrons & numbers, target markers.
* **OCR:** Heat %, fuel %, speed, distance; HUD color profile normalization.
* **Fusion:** Detections + Journal events → `CockpitState {value, conf, age}`.
* **Latency budget:** ≤ 12 ms detection, ≤ 5 ms OCR, ≤ 3 ms fusion, ≤ 10 ms control.

**Detection schema**

```json
{
  "ts": 1690000000.0,
  "screen": {"w":1920,"h":1080},
  "markers": [
    {"type":"target","cx":965,"cy":545,"conf":0.92},
    {"type":"pad_number","bbox":[880,720,940,760],"text":"36","conf":0.88}
  ],
  "gauges": {"heat":0.63,"fuel":0.82,"speed":191,"distance_ls":438}
}
```

---

## 5) Decision Layer

* **HFSM** with re‑entry and recovery states; behavior trees for control flow.
* **Pipelines**

  * *Docking:* `Approach → SlotAlign → InteriorAlign → PadAcquire → FinalDescent → Touchdown`.
  * *Jumping:* `TargetAcquire → AlignToVector → Spool → ChargeGuard → Hyperspace → Cooldown`.
* **Risk engine:** Loosens tolerances and slows control under low FPS/high latency; yields to manual input on conflict.

---

## 6) Skills & Extensibility

**Manifest**

```json
{
  "name": "AutoHaul",
  "version": "0.1.0",
  "triggers": ["Docked","CargoDepotCollect"],
  "permissions": ["navigation","cargo","ui"]
}
```

**Runtime APIs:** `on(event)`, `await(predicate)`, `do(action)`

**Example (pseudo)**

```js
export default skill("AutoHaul", ({on, awaitState, act}) => {
  on("Docked", async () => {
    awaitState(s => s.cargo.free > 0);
    await act.request_docking();
    await act.dock_to("auto");
  });
});
```

**Isolation:** Per‑skill process; CPU/RAM caps; permissioned API surface; hot‑reload.

---

## 7) Setup & Tooling

1. **Repo**

   ```bash
   git clone https://github.com/<your-org>/axis
   ```
2. **Packages**

   ```bash
   # Core
   pip install opencv-python numpy pywin32 mss easyocr pyvjoy websockets requests
   # Optional
   pip install ultralytics onnxruntime
   choco install vjoy
   ```
3. **Data**: Put sample Journal logs in `tests/fixtures/`; curate labeled frames in `data/frames/`.
4. **Dashboard**: self‑signed TLS for Web UI (optional).

---

## 8) Milestones (Merged Roadmap)

### Sprint A (Week 1): **Minimum Viable Cockpit Authority**

* DXGI capture; detector for reticle + heat/fuel bars.
* Motion primitives; closed‑loop `align_to(marker)`.
* Kill switch + watchdog; dashboard with fps/latency/heat/fuel.
  **Acceptance:** Reticle held within ±3% of center for 30 s; throttle target with < 8% overshoot.

### Sprint B (Week 2): **Supercruise & Jump**

* OCR for speed/heat; FSD spool/charge with safeguards; cooldown.
* `jump_next_in_route()` via keybind/panel; 10 consecutive jumps; max heat ≤ 75%.

### Sprint C (Week 3–4): **Docking & Station Ops**

* Slot/chevron/pad detection; `request_docking()`; `dock_to("auto")` with pad acquisition.
* **Acceptance:** 9/10 successful docks from 7 km approach; zero collisions in tests.

---

## 9) Test Plan

* **Unit:** geometry/PID/timers.
* **Perception regression:** mAP on labeled frames; OCR exact‑match rate per HUD theme.
* **Scenario:** replay logs & videos for docking/jumping/scooping; assert timelines and safety triggers.
* **Soak:** 3‑hour travel with jitter; watchdog must not trip; no control runaway.

---

## 10) Observability & Safety

* Web dashboard: state, route step, speeds, heat/fuel, confidence, alarms.
* Panic hotkey immediately disables HID.
* Watchdog suspends outputs on heartbeat gap (>250 ms) or low confidence.

---

## 11) Risks & Mitigations

* **HUD variance** → color‑space normalization, theme‑specific templates.
* **Low FPS** → adaptive control; slower but safe fallback.
* **Detector drift** → continuous regression; online confidence checks.
* **Input conflicts** → pause control when pilot input detected; resume on command.

---

## 12) Definition of Done (Block A)

* Stable PDC loop ≤ 50 ms; dashboard green.
* `align_to`, `throttle`, `brake_to`, `jump_next_in_route` proven.
* Safety systems validated; skill runtime operational with at least 3 actions.

---

## 13) Next Actions

1. Install capture + HID stack; validate 120 fps capture and key pulses.
2. Run detection demo overlay (reticle + heat/fuel OCR).
3. Implement motion primitives with smoothing + jitter.
4. Wire kill switch & watchdog; open tracking issues A‑01/02/03.

*This unified guide supersedes the earlier “AXIS Development Instructions” and v0.2 cockpit‑control plan. Treat this as the single source of truth.*

