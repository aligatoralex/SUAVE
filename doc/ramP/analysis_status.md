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
| 5 | Fin airfoil polar (XFOIL, M2.5 double-wedge) | `analyses/aero/xfoil_runner.py` | DONE | aero-analyst | 2026-07-08 |
| 6 | AVL stability deck (subsonic) | `analyses/aero/avl_builder.py` | DONE | aero-analyst | 2026-07-08 |
| 7 | SU2 external aero (Mach sweep) + transonic CP cross-check | `analyses/cfd/su2_config_template.py` | DONE | aero-analyst | 2026-07-08 |
| 8 | Solid motor selection | `vehicles/ramjet_rocket/motor_database.yaml` | TBD | propulsion-designer | 2026-07-08 |
| 9 | Moments of inertia (Fusion) | — | TBD | vehicle-builder | — |

## Transonic CP cross-check (row 7 validation)

The Barrowman + Rogers-extension stability analysis (row 2) uses a **linear
bridge** (0.8 <= Mach <= 1.2) to interpolate the fin compressibility factor
between subsonic (Prandtl-Glauert) and supersonic (Ackeret) regimes. This is
a low-order engineering approximation with no closed-form theory in the
transonic band.

To validate this assumption, we performed an independent supersonic-linearized
CP estimate at Mach 2.0 (well beyond the transonic band) using Van Dyke
slender-body theory for the nose/transition and Ackeret theory for the fins
(see `analyses/cfd/su2_config_template.py::supersonic_linearized_cp_estimate`).

**Finding (2026-07-08):**

- Barrowman CP at Mach 2.0 (Rogers-extended): **3.943 m** from nose
- Supersonic linearized CP at Mach 2.0: **4.177 m** from nose
- Relative difference: **5.9%**

The two estimates **agree within 6%** at Mach 2.0, well within the expected
tolerance for order-of-magnitude agreement between two different theoretical
bases (Barrowman body-interference + Rogers fin correction vs. linearized
slender-body + Ackeret). This cross-check validates the Barrowman Rogers
extension in the supersonic regime.

**Transonic band (Mach 1.0):** The Barrowman transonic CP at Mach 1.0 is
**4.128 m**, slightly aft of the supersonic values. This is expected: the
linear bridge interpolates between subsonic (more forward) and supersonic
(more aft) CP locations. The transonic estimate is flagged as a **known
open question** requiring CFD or wind-tunnel validation near Mach 1, but
it is not rejected — the linear bridge is a reasonable first-order
approximation for preliminary design.

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
- **Ramjet cycle** (combustor/nozzle performance) — inlet only so far.
