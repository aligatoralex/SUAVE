# MELprop-IADE — Session Handoff (2026-07-08, continuing on claude/melprop-iade-infrastructure-e5b2cn)

Context for a fresh agent picking up this repo. Read `CLAUDE.md` in the repo
root first (mandatory project rules), then this file.

## Repo / branch / PR state

- Repo: `knnmelprop/droneEnv`. Working branch:
  `claude/melprop-iade-infrastructure-e5b2cn` (based on `develop`; the prior
  branch `claude/melprop-iade-infrastructure-rcqzfg` was already merged via
  PR #8 before this session started).
- Open PR: **#11** (`https://github.com/knnmelprop/droneEnv/pull/11`),
  created from this branch — push more commits to update it, do not open a
  new one.
- 3 commits pushed so far this session (newest last):
  1. `fix(ramP): resolve stage-1 thrust peak/mean inconsistency`
  2. `fix(ramP): positive launch-angle trajectory + staged mission; feat: GTM-140 sourced datasheet values`
  3. `feat(ramP): implement xfoil_runner, avl_builder subsonic deck, SU2 Mach-sweep cross-check`
- **Working tree is currently NOT clean** — there is uncommitted WIP for the
  ramjet inlet redesign (see "In-progress / needs finishing" below). Do not
  discard it; it's a real subagent's partial work, not junk.
- `python -m pytest tests/ -v --tb=short` at HEAD (committed state, WIP
  stashed out): **53 passed**. With the uncommitted inlet WIP applied on top:
  **53 passed, 4 failed** (all 4 failures isolated to the inlet redesign, see
  below — nothing else is broken by it).

## What's DONE this session (all committed + pushed, tests green)

1. **Stage-1 thrust peak/mean inconsistency (was BLOCKING).** `SolidRocketPropulsion`
   in `src/schemas/vehicle_schema.py` now has an explicit `thrust_mean_N` field
   (previously only a derived property) alongside `thrust_peak_N`, with two
   validators: peak >= mean always, and mean cross-checked against
   `Isp_sl*mdot*g0` within 2x. `vehicles/ramjet_rocket/vehicle_config.yaml` and
   `motor_database.yaml` updated to consistent SZACOWANY values
   (`thrust_peak_N: 29000`, `thrust_mean_N: 25375`). Still not a real
   datasheet — flagged SZACOWANY throughout.
2. **Booster trajectory launch condition (was BLOCKING).**
   `analyses/trajectory/booster_burnout.py` previously launched at 0 degrees
   (flat) with no lift and impacted the ground before nominal burnout. Now
   launches at 83 degrees (near-vertical) with a zero-lift gravity-turn
   approximation; booster survives to nominal 6 s burnout (Mach 1.23,
   h=1289 m at burnout). The old thrust-inconsistency warning logic (now
   obsolete since the schema validates it) was cleaned up.
3. **Staged mission.** New `workflows/ramp_staged_mission.py` builds a 3-segment
   mission via `core/mission_builder.py`'s `MissionBuilder`: booster
   boost/burnout -> staging_event (booster burnout state fed forward as
   initial conditions) -> ramjet cruise takeover (cruise segment is a
   documented stub/placeholder, not a full ramjet-cruise ODE integration —
   that's still open work if wanted). Tests in `tests/unit/test_missions_staged.py`.
4. **GTM-140 (Project A) real datasheet values.** Sourced via web search from
   a peer-reviewed paper (DOI 10.1515/eng-2015-0053): thrust 140 N (confirmed
   the existing placeholder was already correct), mass flow 0.35 kg/s,
   compression ratio 2.8:1, EGT 700 degC (973.15 K), diameter 110 mm, length
   265 mm, max RPM 120,000. Added as new optional fields on `TurbojetConfig`
   in `src/schemas/vehicle_schema.py`. `mass_kg` and `sfc_kg_per_Ns` are
   **deliberately still TBD** — no reliable public source found for the
   GTM-140 specifically (a superficially similar number from a *different*
   engine class was found and explicitly NOT reused — don't fabricate these,
   a real Jetpol datasheet or manufacturer contact is needed).
   `wing.aspect_ratio: 8.0` is also still TBD (it's the team's own airframe
   design, not a published engine spec — nothing to source from the web).
5. **Ixx/Iyy/Izz moments of inertia.** Confirmed this cannot be obtained by an
   agent — Fusion 360 only exposes the inertia tensor via its GUI Physical
   Properties panel, not its scripting API. Documented precise manual
   extraction steps in `vehicles/ramjet_rocket/vehicle_config.yaml`'s `tbd:`
   list and `doc/ramP/analysis_status.md`. Do NOT estimate/approximate this
   with a simplified mass model as a substitute — that would misrepresent a
   placeholder as real data (CLAUDE.md rule #9). Needs a human with Fusion
   360 open.
6. **Aero stubs implemented.**
   - `analyses/aero/xfoil_runner.py`: fin double-wedge polar — Ackeret
     linearized supersonic theory at M2.5 cruise design point, XFOIL
     subprocess path (guarded by `shutil.which`) with analytical flat-plate
     fallback for the subsonic boost-initiation/recovery regime.
   - `analyses/aero/avl_builder.py`: AVL deck generator for the ramjet
     rocket's fins, scoped to the low-speed boost-initiation/recovery
     envelope only (Mach < 0.6 enforced, same as the wing wrapper) — this is
     intentionally NOT for Project A, and NOT for the supersonic cruise.
   - `analyses/aerodynamics/avl_wrapper.py`: wired an actual AVL subprocess
     path end-to-end for the Project A (GTM-140) wing, with the existing
     `helmbold_cl_alpha` analytical fallback kept intact and still what
     actually runs (no `avl`/`xfoil`/`SU2_CFD` binaries are installed in this
     sandbox — every fallback path is what the test suite exercises, the
     subprocess paths are implemented+parseable but untested against a real
     binary).
   - `analyses/cfd/su2_config_template.py`: Mach-sweep `.cfg` generation plus
     a supersonic-linearized-theory CP estimate used to cross-check
     `analyses/stability/barrowman_stability.py`'s transonic CP bridge.
     **Finding**: Barrowman and the independent linearized estimate agree
     within ~6% at Mach 2.0 (validates the supersonic regime). The Mach~1
     linear-bridge region itself is still NOT validated by any closed-form
     theory or CFD — flagged as an open question in
     `doc/ramP/analysis_status.md`, not silently trusted.

## In-progress / needs finishing (uncommitted WIP in the working tree right now)

**Ramjet inlet redesign for MIL-E-5007 (task was: redesign as 2-3 cone
external compression).** A subagent was mid-implementation when it hit an
API session limit and stopped mid-write (not corrupted — the file compiles
fine, just functionally incomplete). Current state:

- `analyses/propulsion/inlet_performance.py`: added a generalized
  `multi_cone_recovery_chain` (N sequential oblique shocks + terminal normal
  shock + diffuser efficiency, keeping the original single-cone
  `inlet_recovery_chain` intact/untouched), an angle-optimizer, and a new
  `MultiConeInletPerformanceAnalysis` class alongside the original
  single-cone `InletPerformanceAnalysis` (both should remain queryable —
  the single-cone one represents the Fusion-CAD-verified as-built spike,
  the multi-cone one is explicitly a redesign proposal not yet reflected in
  the CAD).
- **Key finding already reached by the WIP before it stopped**: a 2-cone
  design cannot reach MIL-E-5007 recovery (eta_std=0.870) at the M2.5 design
  point — best achieved was eta~0.798 (2-cone) / eta~0.849 (3-cone), both
  still short. The WIP's own in-code analysis note (citing Seddon &
  Goldsmith, "Intake Aerodynamics", 1999, Sec 4.3) concludes **4+ cones are
  the minimum needed** to clear the standard at this Mach, and had started
  adding 4-cone placeholder angles (clearly marked SZACOWANY) when it was
  cut off.
- **What's failing right now** (4 tests in `tests/unit/test_propulsion_inlet.py`):
  `test_optimize_multi_cone_angles_2cone_meets_mil_e_5007`,
  `test_optimize_multi_cone_angles_3cone_meets_mil_e_5007`,
  `test_multi_cone_inlet_analysis_design_point_meets_mil_e_5007`,
  `test_multi_cone_inlet_analysis_3cone_design` — all failing because they
  assert a 2- or 3-cone design meets MIL-E-5007, which the WIP's own physics
  now says is not achievable. **These tests need to be updated to target a
  4-cone (or more) design** to match the physically-justified conclusion,
  not have the physics fudged to fit the old 2/3-cone test expectations.
  Everything else (22 other tests in that file) passes.
- To finish: pick up `analyses/propulsion/inlet_performance.py` and
  `tests/unit/test_propulsion_inlet.py` as currently modified in the working
  tree, extend/finish the 4-cone angle optimization so
  `eta_inlet >= mil_e_5007_eta_std(2.5)` actually holds, update the 4 failing
  tests to assert against the number of cones that's actually achievable
  (do not lower the MIL-E-5007 bar to make old tests pass), then run
  `python -m pytest tests/ -v --tb=short` and confirm fully green before
  handing back to the orchestrator for commit (do not run git yourself if
  you are a subagent in this workflow — the orchestrator commits).

## Working rules recap (see CLAUDE.md for full text)

SI unit suffixes in field/variable names; type hints; Google-style
docstrings with theory references on physics code; file header
`# MELprop-IADE | <module.path> | v0.1.0` on new files; run
`python -m pytest tests/ -v --tb=short` after every change and keep it
green; never rewrite `trunk/SUAVE/` or `core/` (extend via subclassing);
AVL only for Mach < 0.6 and |alpha| < 15 deg, never for the ramP supersonic
cruise; mark unsourced numbers `# SZACOWANY`/`# TBD` and never present them
as validated; delegate to the matching subagent role
(aero-analyst / propulsion-designer / vehicle-builder / mission-planner /
code-reviewer / docs-writer per `.claude/agents/`); subagents write files
only and never run git — the orchestrator commits and pushes.
