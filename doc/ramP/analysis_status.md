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
| 5 | Fin airfoil polar (XFOIL, M2.5 double-wedge) | `analyses/aero/xfoil_runner.py` | STUB | aero-analyst | 2026-07-08 |
| 6 | AVL stability deck (subsonic) | `analyses/aero/avl_builder.py` | STUB | aero-analyst | 2026-07-08 |
| 7 | SU2 external aero (Mach sweep) | `analyses/cfd/su2_config_template.py` | STUB | aero-analyst | 2026-07-08 |
| 8 | Solid motor selection | `vehicles/ramjet_rocket/motor_database.yaml` | TBD | propulsion-designer | 2026-07-08 |
| 9 | Moments of inertia (Fusion) | — | TBD | vehicle-builder | — |
| 10 | Multi-cone inlet redesign (4-cone, M2.5) | `analyses/propulsion/inlet_performance.py` | DONE | propulsion-designer | 2026-07-08 |
| 11 | Ramjet cycle L2 (combustor+nozzle) | `analyses/propulsion/ramjet_cycle.py` | DONE | propulsion-designer | 2026-07-08 |
| 12 | Staged mission cruise design point | `workflows/ramp_staged_mission.py` | DONE | mission-planner | 2026-07-08 |
| 13 | Static margin review (Barrowman) | `doc/ramP/static_margin_review.md` | DONE | aero-analyst | 2026-07-08 |
| 14 | Stability margin report (Barrowman vs Teltik 2024 CFD) | `doc/ramP/stability_margin_report.md` | DONE | aero-analyst | 2026-07-09 |
| 15 | Inlet completeness audit (Night-2 Phase 1b) | `tests/unit/test_propulsion_inlet.py` | DONE | code-reviewer | 2026-07-09 |
| 16 | Combustor+nozzle Grzywka model (CC→NT→NE, Thi/Th1/Th2) | `analyses/propulsion/combustor_nozzle_cycle.py` | **BLOCKED_BY_BUDGET** | propulsion-designer | 2026-07-09 |
| 17 | Cruise wiring to Grzywka model (Night-2 Phase 3b) | `workflows/ramp_staged_mission.py` | BLOCKED_BY_BUDGET | mission-planner | 2026-07-09 |
| 18 | Movable-inlet actuation params (Night-2 Phase 4b) | `analyses/propulsion/inlet_performance.py` | BLOCKED_BY_BUDGET | propulsion-designer | 2026-07-09 |

## Night-2 checkpoint (2026-07-09, budget guard at 80%)

Night-2 run was halted **cleanly** mid **Phase 2b** by the budget guard firing
at 80% of the usage window. The Phase 2b subagent (propulsion-designer,
opus-tier) was stopped while still in its **read-only exploration** step —
**before any file was written**. Verified clean stop: `git status` tree
clean, no partial/dangling files, full suite **80/80 tests green**.

**Resume point:** next session should resume **Night-2 Phase 2b** from its
full task spec below (do not re-diagnose, do not restart from Phase 0):

- Create `analyses/propulsion/combustor_nozzle_cycle.py` +
  `tests/unit/test_propulsion_combustor_nozzle.py`.
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
