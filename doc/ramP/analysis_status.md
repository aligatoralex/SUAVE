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

## Open data gaps
- **Motor datasheet** — stage-1 propulsion is still `SZACOWANY` (estimated).
  RESOLVED 2026-07-08: `thrust_peak_N`/`thrust_mean_N` are now independent,
  schema-validated fields (peak >= mean enforced, cross-checked against
  Isp*mdot*g0); the previous 12 kN "peak" was below the impulse-consistent
  ~25.4 kN mean, which is physically impossible. Still needs a real
  R-13-class datasheet to replace the SZACOWANY values.
- **Moments of inertia** Ixx/Iyy/Izz — not available via the Fusion API.
- **Ramjet cycle** (combustor/nozzle performance) — inlet only so far.
