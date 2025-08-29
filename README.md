# Automated Xenial Intelligence System (AXIS)

**Elite Dangerous personal‑assistant framework**

---

## 1 · Why AXIS Exists

| Aim                                                                                                    | Benefit                                                  |
| ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| Autonomous handling of long, repetitive chores (neutron‑highway travel, cargo loops, carrier fueling). | Frees the pilot to focus on exploration and combat.      |
| Drop‑in plugin system (“skills”) so anyone can add new routines with minimal code.                     | Community keeps AXIS evolving without touching the core. |
| 100 % EULA‑safe—reads only Journal files, outputs only HID/VoiceAttack commands.                       | Protects CMDR accounts from bans.                        |

---

## 2 · Architecture Snapshot

```
┌────────────┐   Journal Events     ┌──────────────┐
│  Game Client│ ───────────────────▶│  Input Layer │ (EliteAPI)
└────────────┘                      └─────▲────────┘
                                         │ JSON bus
                    ┌──────────────┐     │
Virtual HID (vJoy) ◀│  Output Layer│◀────┘
VoiceAttack macros  └──────────────┘
          ▲
          │ commands
┌──────────────────────┐
│  AXIS Core (Kernel)  │  ➜ FSM, Watchdog, Skill Loader
└─────────▲────────────┘
          │
   sandboxed skills
      (TS / PY)
```

---

## 3 · Foundation Milestone “Block 0”

| Layer          | Deliverable                                                                                |
| -------------- | ------------------------------------------------------------------------------------------ |
| **Input**      | Stream live events with [EliteAPI](https://github.com/EliteAPI/EliteAPI) → unified JSON.   |
| **Planner**    | Remote call to [Spansh neutron router](https://spansh.co.uk/) with offline fallback.       |
| **Actuation**  | Inject stick & button events via [vJoy](https://vjoystick.sourceforge.io/) or VoiceAttack. |
| **FSM**        | Jump → scoop monitor → next waypoint. Safety hooks: interdiction, overheating.             |
| **Skill Hook** | `skills/` folder; each plugin exports `{ triggers, actions }`.                             |
| **Dashboard**  | WebSocket page showing waypoint, fuel %, heat %, watchdog timer.                           |

---

## 4 · Setup Checklist

1. **Clone repo**

   ```bash
   git clone https://github.com/<your-org>/axis
   ```
2. **Install tools**

   ```bash
   pip install eliteapi websockets requests
   choco install vjoy        # Windows virtual HID
   ```
3. **Generate self‑signed TLS cert** for WebSocket dashboard if desired.
4. **Copy example Journal logs** into `tests/fixtures/` for playback unit tests.

---

## 5 · Day‑by‑Day Kick‑off Plan

| Day | Target                                                              |
| --- | ------------------------------------------------------------------- |
| 0   | Journal listener prints events to console.                          |
| 1   | Wrap events into internal JSON bus; write first unit test (pytest). |
| 2   | Send a dummy throttle pulse via vJoy; confirm in game.              |
| 3   | Fetch Sol → Colonia neutron route from Spansh; store as JSON.       |
| 4   | Build finite‑state machine to iterate waypoints.                    |
| 5   | Add heat & fuel guards; watchdog kills outputs if stall > 3 s.      |
| 6   | Skill loader runs a `hello_skill.py` that logs Dock events.         |
| 7   | Package `axis-core.exe`; push README + SDK stubs to GitHub.         |

---

## 6 · Extensibility Guidelines

* **Skill Manifest**

  ```json
  {
    "name": "AutoHaul",
    "version": "0.1.0",
    "triggers": ["Docked", "CargoDepotCollect"],
    "permissions": ["navigation", "cargo"]
  }
  ```
* **Sandbox**: Each skill executes in its own process (Py) or WebAssembly worker (TS) with capped CPU & RAM.
* **Versioned Schemas**: Event JSON spec lives in `/schema/v1.x/`—never break backwards compatibility.
* **Distribution**: Community registry `axis-skills.json`; `axis install neutron-hauler@1.2.0`.

---

## 7 · Robustness & Safety

* Panic toggle—one joystick button disables all outputs instantly.
* Static AST scan rejects skills performing file writes outside `~/.axis`.
* Continuous integration replays 50 + edge‑case Journal logs (heat, mis‑plot, emergency drop).
* Kernel heartbeat monitored by watchdog; if no beat in 3 s, outputs disabled and desktop notification raised.

---

## 8 · Stretch‑Goal Roadmap

1. Natural‑language commander: “Plot a route to the nearest Guardian site and farm 50 blueprints.”
2. YOLO‑tiny vision assist for pad alignment on outposts.
3. Federated telemetry sharing to optimise heat‑management heuristics.
4. Latency‑aware randomised jitter to mimic human imperfection.

---

## 9 · Next Action

> **Run the Day 0 script, confirm event stream, and open your first pull request.**
>
> Once the “Block 0” milestone passes integration tests, AXIS can already ferry a ship 22 kly hands‑free—forming the bedrock for unlimited player‑made routines.

Fly safe, CMDR. **o7**
