# MELprop ramP — Analysis Status

Two-stage supersonic rocket (solid booster + ramjet cruise). Geometry from
Fusion Assembly v6 (`vehicles/ramjet_rocket/fusion_extraction_v6.yaml`).

Status legend: **DONE** (implemented + run) · **STUB** (scaffold + TODO) ·
**TBD** (not started / needs external data).

| # | Analysis | Module | Status | Owner | Date |
|---|----------|--------|--------|-------|------|
| 1 | Vehicle config + schema (v0.2.0) | `src/schemas/vehicle_schema.py`, `vehicles/ramjet_rocket/vehicle_config.yaml` | DONE | vehicle-builder | 2026-07-08 |
| 2 | Static stability (Barrowman + Rogers) | `analyses/stability/barrowman_stability.py` | DONE | aero-analyst | 2026-07-08 |
| 3 | Boost-phase trajectory (3-DOF) | `analyses/trajectory/booster_burnout.py` | DONE | mission-planner | 2026-07-08 |
| 4 | Ramjet inlet (conical spike, M2.5) | `analyses/propulsion/inlet_performance.py` | DONE | propulsion-designer | 2026-07-08 |
| 5 | Fin airfoil polar (XFOIL, M2.5 double-wedge) | `analyses/aero/xfoil_runner.py` | DONE | aero-analyst | 2026-07-09 |
| 6 | AVL stability deck (subsonic) | `analyses/aero/avl_builder.py` | STUB | aero-analyst | 2026-07-08 |
| 7 | SU2 external aero (Mach sweep) | `analyses/cfd/su2_config_template.py` | IN_PROGRESS | aero-analyst | 2026-07-09 |
| 8 | Solid motor selection | `vehicles/ramjet_rocket/motor_database.yaml` | IN_PROGRESS | propulsion-designer | 2026-07-09 |
| 9 | Moments of inertia (Fusion) | — | TBD | vehicle-builder | — |
| 10 | Multi-cone inlet redesign (4-cone, M2.5) | `analyses/propulsion/inlet_performance.py` | DONE | propulsion-designer | 2026-07-08 |
| 11 | Ramjet cycle L2 (combustor+nozzle) | `analyses/propulsion/ramjet_cycle.py` | DONE | propulsion-designer | 2026-07-08 |
| 12 | Staged mission cruise design point | `workflows/ramp_staged_mission.py` | DONE | mission-planner | 2026-07-08 |
| 13 | Static margin review (Barrowman) | `doc/ramP/static_margin_review.md` | DONE | aero-analyst | 2026-07-08 |
| 14 | Stability margin report (Barrowman vs Teltik 2024 CFD) | `doc/ramP/stability_margin_report.md` | DONE | aero-analyst | 2026-07-09 |
| 15 | Inlet completeness audit (Night-2 Phase 1b) | `tests/unit/test_propulsion_inlet.py` | DONE | code-reviewer | 2026-07-09 |
| 16 | Combustor+nozzle Grzywka model (CC→NT→NE, Thi/Th1/Th2) | `analyses/propulsion/combustor_nozzle_cycle.py` | DONE | propulsion-designer | 2026-07-09 |
| 17 | Cruise wiring to Grzywka model (Night-3 Phase 3) | `workflows/ramp_staged_mission.py` | DONE | mission-planner | 2026-07-09 |
| 18 | Movable-inlet actuation params (Night-3 Phase 4) | `analyses/propulsion/inlet_actuation.py` | DONE | propulsion-designer | 2026-07-09 |
| 19 | Stability reconciliation (geometry audit + fin-span sensitivity sweep, Night-3 Phase 5) | `doc/ramP/stability_reconciliation.md` | DONE | aero-analyst | 2026-07-09 |
| 20 | Launch-angle sweep (5–30°, recommended 5° via booster_burnout.py) | `analyses/trajectory/booster_burnout.py::run_launch_angle_sweep` | DONE | mission-planner | 2026-07-09 |
| 21 | Inlet actuation schedule (4-cone, Ma 2.4–3.5 MIL-E-5007 band, Δθ per cone) | `analyses/propulsion/inlet_actuation.py` | DONE | propulsion-designer | 2026-07-09 |

## Night-2 checkpoint (2026-07-09, budget guard at 80%)

Night-2 run was halted **cleanly** mid **Phase 2b** by the budget guard firing
at 80% of the usage window. The Phase 2b subagent (propulsion-designer,
opus-tier) was stopped while still in its **read-only exploration** step —
**before any file was written**. Verified clean stop: `git status` tree
clean, no partial/dangling files, full suite **80/80 tests green**.

**Resume point:** next session should resume **Night-2 Phase 2b** from its
full task spec below (do not re-diagnose, do not restart from Phase 0):

- Create `analyses/propulsion/combustor_nozzle_cycle.py` <!-- TODO: dead link, target missing as of 2026-07-09 --> +
  `tests/unit/test_propulsion_combustor_nozzle.py` <!-- TODO: dead link, target missing as of 2026-07-09 -->.
- Model: Grzywka 2022, stations **1 → 2 → 21 → 3** (CC → NT → NE).
- Loss coefficients: `pi_CC = 0.8924` (1→2), `pi_nozzle = 0.97` (2→3).
- Nozzle throat area **D21 is dynamic** (a function of `V`, `H`), with
  `Ma_throat = 1` always enforced — never hard-code D21 as a constant.
- Report **three thrust models**: Thi, Th1, Th2 (Grzywka §6.2.2) — all three,
  always, never collapse to a single thrust number.
- Cross-check against a Brayton-cycle T2 estimate; flag if delta > 5%.
- Log V3 vs Teltik 2024 CFD (~1047 m/s at Ma 2.5 / 6000 m) delta.
- Check the nozzle area ratio against the YAML value (4.0).
- **Requires opus-tier** per the run plan — do not substitute sonnet for this
  phase.

## Night-3 checkpoint (2026-07-09)

Night-3 run completed **cleanly, full budget used** (not cut mid-phase). Phases 2–7
executed (P1 combustor already DONE via PR #13). Full test suite **154/154 green**.
Tree clean. Six commits, one per phase:

| Phase | Description | Commit | Result |
|-------|-------------|--------|--------|
| P2 | Combustor + nozzle Grzywka cycle | 546a55e7 | Th1=12107.9N, V3=1474.3 m/s; CFD delta +40.8% (HUMAN_REVIEW) |
| P3 | Cruise wiring (switch to Th1) | 8e65b39d | Thrust margin ±10121N (drag CD0=0.35) / ±9656N (Teltik CFD) |
| P4 | Inlet actuation 4-cone schedule | e7629e76 | MIL-E-5007 on [2.4, 3.5] Mach, Δθ = 3.5/8.3/15.2/24.3 deg per cone |
| P5 | Fin polar (Ackeret fallback) | 3584f0fa | CL=0.1523, CD with τ=0.1697 (Fusion t/c) at Ma2.5 α=5°; XFOIL pending binary |
| P6 | Motor database (3 HTPB candidates) | 9a3c00b8 | 20–30 kN mean, 5–8 s, Isp 205–230 s, all SZACOWANY |
| P7 | Launch-angle sweep (5–30°) | 8a05c714 | Recommended 5° (burnout alt 45.3 m, q_max 131.75 kPa); 0° non-viable |

**Work item status update:**
- WP 5 (XFOIL fin polar) → **DONE** (Ackeret fallback; full XFOIL delegation pending binary availability)
- WP 7 (SU2 Mach sweep) → **IN_PROGRESS** (generator module complete; runner pending SU2 binary)
- WP 8 (Motor selection) → **IN_PROGRESS** (3 candidates populated in motor_database.yaml; awaiting real R-13 datasheet)

**Next session (Night-4) recommended priorities:**
1. AVL builder stub → subsonic deck generation (WP 6 subsonic CLα/Cmα).
2. SU2 runner once binary available (WP 7; Mach [0.8–3.0] external aero).
3. Real motor datasheet ingestion and trajectory re-run (WP 8).
4. Moments of inertia extraction from Fusion GUI (WP 9).
5. Nozzle Laval design decision (cylindrical stub 1.0 ratio vs YAML 4.0 ratio).
6. Housekeeping: add `runs/` to `.gitignore` (team decision pending).

**⚠️ HUMAN_REVIEW flags for Night-4:**
- V3 exit velocity CFD delta +40.8% — exceeds known 20–30% MATLAB-vs-CFD scatter band.
- Fin-span sign-flip standing (see static_margin_review.md).

## Open data gaps
- **Motor datasheet** — stage-1 propulsion is still `SZACOWANY` (estimated).
  RESOLVED 2026-07-08: `thrust_peak_N`/`thrust_mean_N` are now independent,
  schema-validated fields (peak >= mean enforced, cross-checked against
  Isp*mdot*g0); the previous 12 kN "peak" was below the impulse-consistent
  ~25.4 kN mean, which is physically impossible. Still needs a real
  R-13-class datasheet to replace the SZACOWANY values.
- **Moments of inertia** Ixx/Iyy/Izz — Fusion 360 exposes the inertia tensor
  ONLY in the GUI Physical Properties panel, not via its scripting API. Manual
  extraction required: open Fusion Assembly v6, right-click main component →
  "Physical Properties", copy Ixx/Iyy/Izz values (units: kg·m²) from the panel
  into `mass_properties:` section of `vehicle_config.yaml`. Cannot be automated.
- **Ramjet cycle** (combustor/nozzle performance) — RESOLVED 2026-07-08 at L2 fidelity (station 0-2-4-9 cycle; single-method result, MATLAB baseline unavailable, CFD delta +20-30% open).
- **Nozzle geometry discrepancy** — vehicle_config.yaml nozzle_area_ratio 4.0 vs Fusion v6 cylindrical stub (expansion_ratio 1.0); thrust 12.31 kN (matched) vs 9.85 kN (cylindrical). Needs Laval nozzle design decision.
- **Fin span suspect** (static margin 10.08 cal, ~7-8x span reduction would hit 1.5-2 cal) — likely Fusion export artifact, needs team review (see static_margin_review.md).
