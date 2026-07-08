# MELprop ramP — Preliminary Analysis Report

**Date:** 2026-07-08
**Vehicle:** MELprop-Ramjet-Missile — two-stage supersonic rocket (solid booster + ramjet cruise)
**Geometry source:** Fusion 360 Assembly v6 (CORRECTED: cm→m, Y-axis longitudinal)
**Fidelity:** low-order engineering estimates (L0–L1) — **not** flight-safety sign-off.

---

## 1. Vehicle Dimensions (from Fusion)

| Parameter | Value | Source |
|---|---|---|
| Total length | 4.377 m | Fusion Y-bbox |
| Max transverse dimension | 0.639 m | Fusion X/Z-bbox |
| Body diameter (aero ref) | 0.250 m | body |
| Nose (conical spike) | L 0.293 m, base Ø 0.150 m | inlet_cone |
| Total mass | 355.02 kg | Fusion physics |
| CG from nose | 1.6084 m (36.7 % L) | Fusion |
| Booster assembly | L 2.089 m, bbox Ø 1.809 m (incl. PRD-240 wings) | booster |
| Fins | 4× rectangular, span 0.6685 m, chord 0.1768 m, sweep 0° | stabilizers |
| Ramjet capture area | 0.04909 m² (= π/4·0.250²) | inlet_Mk1 |

> **Booster bbox note.** The 1.809 m booster "diameter" is a bounding-box artifact of the
> protruding PRD-240 reference wings; the aerodynamic reference diameter is the 0.250 m body.

---

## 2. Stability Assessment

Method: subsonic Barrowman (nose + 0.150→0.250 shoulder transition + cruciform fins with
Hoerner body-interference) plus a Rogers-style transonic/supersonic fin-slope correction.
Full data: [`analyses/stability/barrowman_results.json`](../../analyses/stability/barrowman_results.json).

| Quantity | Value |
|---|---|
| CP (subsonic, M→0) | **4.128 m** from nose |
| CP (transonic, M=1.0) | 4.155 m from nose |
| CG | 1.6084 m from nose |
| Static margin (subsonic) | **10.08 cal** |
| Fineness ratio L/d | 17.51 |
| Required SM = L/(10·d) | 1.75 cal |
| Margin over requirement | +8.33 cal |
| **Verdict** | ✅ **PASS** |

The huge exposed fin span (2.67× body diameter) makes the fins dominate CN_α, driving CP far
aft and yielding a very large — arguably *over*-stable — margin. Physically this fin set reads
more like a booster-glide surface than a dart fin.

![CP vs Mach](../../analyses/stability/cp_vs_mach.png)

---

## 3. Boost Phase Trajectory

Method: 3-DOF point mass (vertical plane), `scipy.solve_ivp` RK45, manual ISA atmosphere,
DATCOM-style CD, mass depletion. Full data:
[`analyses/trajectory/burnout_state.json`](../../analyses/trajectory/burnout_state.json).

| Quantity | Value |
|---|---|
| Thrust used | **25.4 kN** (impulse-consistent, Isp·ṁ·g₀) |
| Burn cutoff | **t = 4.53 s** (⚠️ ground impact, before 6 s burnout) |
| Velocity at cutoff | 350 m/s (**Mach 1.03**) |
| Altitude at cutoff | ≈ 0 m (from h₀ = 100 m) |
| Max dynamic pressure | **75.0 kPa** |
| Range at cutoff | 771 m |

> ⚠️ **0° horizontal launch is not viable as modeled.** With gravity, no lift, and h₀ = 100 m,
> the rocket sinks to the ground at t ≈ 4.5 s — *before* the nominal 6 s burnout. A real launch
> needs a positive launch angle and/or lift. The along-track state is reported honestly at impact.
>
> ⚠️ **Thrust inconsistency.** `vehicle_config.yaml` lists `thrust_peak_N = 12000`, but 75 kg of
> propellant over 6 s at Isp 207–230 s implies a **mean** thrust of ~25.4 kN — a peak below the
> mean is impossible. The sim used the impulse-consistent 25.4 kN and ignored the 12 kN figure.

![Boost phase](../../analyses/trajectory/boost_phase.png)

---

## 4. Inlet Performance

Method: axisymmetric conical-spike inlet at design Mach 2.5 — oblique shock (θ-β-M weak
solution) + terminating normal shock + diffuser efficiency, vs the MIL-E-5007 standard.
Full data: [`analyses/propulsion/inlet_results.json`](../../analyses/propulsion/inlet_results.json).

| Quantity | Value |
|---|---|
| Spike half-angle | 14.36° |
| Oblique shock angle β | 36.25° |
| Mach after oblique / normal shock | 1.90 → 0.60 |
| Pressure recovery (oblique·normal·η_diff) | 0.937 · 0.767 · 0.92 = **η_inlet 0.661** |
| MIL-E-5007 standard | η_std 0.870 |
| Mass flow at design (10 km ISA) | 15.17 kg/s |
| **Verdict** | ❌ **FAIL** (margin −0.210) |

A single-cone (one oblique + one normal shock) spike is minimum-part-count and predictably falls
short of MIL-E-5007 at M 2.5. This motivates a **multi-shock (2–3 cone) or isentropic spike** for
a production inlet. The θ-β-M wedge stand-in for the true Taylor–Maccoll conical shock makes the
reported recovery slightly *conservative*.

![Inlet recovery](../../analyses/propulsion/inlet_recovery.png)

---

## 5. Open Issues & Next Steps

- [ ] Replace **R-13 mockup** with a real motor datasheet (resolves the 12 kN vs 25 kN thrust conflict).
- [ ] Re-run the trajectory with a **positive launch angle** and/or a lift model (0° horizontal is non-viable).
- [ ] Redesign the **ramjet inlet** (multi-shock/isentropic spike) to meet MIL-E-5007 at M 2.5.
- [ ] Redesign the **cylindrical nozzle** (area ratio 1.0) into a Laval nozzle for the cruise stage.
- [ ] Run **XFOIL** fin polar at M 2.5 (double-wedge) — `analyses/aero/xfoil_runner.py` (STUB).
- [ ] Generate the **AVL** subsonic deck, compute Cmα / CLα — `analyses/aero/avl_builder.py` (STUB).
- [ ] Run **SU2** external-aero Mach sweep [0.8–3.0] — `analyses/cfd/su2_config_template.py` (STUB).
- [ ] Extract **moments of inertia** Ixx/Iyy/Izz from the Fusion GUI (not available via API).
- [ ] Model the full **ramjet cycle** (combustor + nozzle), currently inlet-only.
- [ ] Wind-tunnel / water-tunnel (WUT) validation of the transonic CP estimate.

## 6. TBD Parameters (from `vehicle_config.yaml`)

- Stage-1 motor datasheet: Isp, thrust curve, propellant mass — currently `SZACOWANY` (estimated).
- Stage-2 ramjet `design_mach` — final decision pending (2.5 assumed).
- Moments of inertia Ixx/Iyy/Izz — from Fusion GUI.
- Combustor exit temperature — pending pyCycle cycle analysis (2000 K assumed).

---

*Generated by the MELprop-IADE analysis pipeline (Barrowman stability, 3-DOF trajectory, conical-spike inlet).
All results are low-order preliminary estimates pending CFD / wind-tunnel corroboration and real motor data.*
