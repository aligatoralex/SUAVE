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
