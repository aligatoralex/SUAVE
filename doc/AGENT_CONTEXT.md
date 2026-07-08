# MELprop-IADE — Agent Context & Repository Handoff

> Onboarding for the next agent session. Read this together with the root
> [`CLAUDE.md`](../CLAUDE.md) (architecture + hard rules) and
> [`doc/ramP/analysis_status.md`](ramP/analysis_status.md) (live task tracker).
> **Last updated: 2026-07-08, ~22:20 UTC.** This file supersedes the version of
> itself merged into `develop` via PR #10 (2026-07-08 23:10 CEST/21:10 UTC),
> which described the repo state *before* the fixes in section 6 below — if
> you're reading a copy of this file that still says the inlet FAILS
> MIL-E-5007 or the launch angle is 0 degrees, you are reading a stale copy;
> trust this one (or `git log` on `doc/AGENT_CONTEXT.md` for the newest).

---

## 1. What this repo is

A fork of **SUAVE** (aircraft-design toolbox, in `trunk/SUAVE/` — **do not
modify**) extended by the KNN MELprop student club (Politechnika Warszawska)
into an integrated design environment (**MELprop-IADE**) for two vehicles:

- **Project A — GTM-140 drone**: fixed-wing UAV with the Jetpol GTM-140
  miniature **turbojet** (not a turbofan — no propeller). Subsonic,
  VLM/AVL + XFOIL.
- **Project B — "ramP" rocket**: two-stage supersonic rocket — solid booster
  (stage 1) + ramjet cruise (stage 2), design Mach 2.5. Empirical/DATCOM-style
  aero (AVL is banned for the supersonic part), conical-spike inlet, staging
  at booster burnout.

The repo also carries teaching material merged in from a former `droniada`
branch: `Tutorials252/`, `Tutorials-2.3.1/`, `student_competition/` (Droniada
Sztafeta framework), `.devcontainer/` (Codespaces). That material is
unrelated to the MELprop-IADE work and hasn't been touched this session.

---

## 2. Repository layout (MELprop-IADE additions)

```
core/                         # Foundation — EXTEND via inheritance, never rewrite
  component_base.py           #   BaseComponent, BaseAnalysis, FidelityLevel(L0-L3),
                              #   AnalysisResults, ComponentRegistry
  vehicle_factory.py          #   SUAVE vehicle factory (guarded SUAVE import)
  mission_builder.py          #   Solver-agnostic mission-segment builder (MissionBuilder)
  solver_registry.py          #   External-solver registry (AVL, XFOIL, ...)
src/schemas/vehicle_schema.py # Pydantic v2 config models (schema v0.2.0), extra="forbid"
vehicles/
  gtm140_drone/vehicle_config.yaml
  ramjet_rocket/vehicle_config.yaml         # schema-validated engineering config
  ramjet_rocket/fusion_extraction_v6.yaml   # RAW Fusion export (source of truth for geometry)
  ramjet_rocket/motor_database.yaml         # candidate solid motors
analyses/
  aerodynamics/avl_wrapper.py    # AVLAnalysis — Project A wing, AVL subprocess + Helmbold fallback — DONE
  stability/barrowman_stability.py   # Barrowman + Rogers CP/static margin — DONE
  trajectory/booster_burnout.py      # 3-DOF boost sim (scipy) — DONE (launch angle fixed, see §6)
  propulsion/inlet_performance.py    # conical-spike inlet vs MIL-E-5007 — DONE (single-cone) +
                                      #   IN-PROGRESS multi-cone redesign, see §7 — uncommitted WIP
  aero/xfoil_runner.py               # fin double-wedge polar (Ackeret + XFOIL fallback) — DONE
  aero/avl_builder.py                # AVL deck for ramP fins, low-speed only — DONE
  cfd/su2_config_template.py         # SU2 Mach-sweep config + transonic CP cross-check — DONE
workflows/
  ramp_staged_mission.py         # 3-segment staged mission via MissionBuilder — DONE (cruise segment is a stub)
  staged_mission_profile.json    # generated output of the above
tests/unit/                    # pytest — see file list in §4
doc/
  AGENT_CONTEXT.md              # this file
  ramP/analysis_status.md       # live per-analysis status table, keep updated
  ramP/preliminary_analysis_report.md  # STALE — written before this session's fixes, numbers not refreshed
  ramP/session_handoff_2026-07-08.md   # narrower dated handoff written mid-session, largely superseded by this file
.claude/agents/                # 6 subagent definitions (see §9)
```

---

## 3. Environment setup (deps are NOT vendored)

Fresh containers have **none** of the Python deps installed. Install before
doing anything:

```bash
pip install pydantic pytest pyyaml numpy scipy matplotlib
```

- **SUAVE** (from `trunk/`) is optional for unit tests — imports in `core/`
  are guarded (`try/except ImportError`); schema/analysis modules run without it.
- **AVL / XFOIL / SU2 / gmsh / pyCycle / OpenMDAO** binaries are **not**
  installed in this sandbox. Every analysis that would call one of these has
  an analytical fallback (guarded by `shutil.which(...)`), and the test suite
  exercises the fallback paths only — the subprocess code paths are written
  and believed correct but have never been run against a real binary.
- Python 3.11 is what's actually on PATH in this container; `pytest` itself
  may live in an isolated `uv` tool venv at `/root/.local/bin/pytest` that
  does NOT have the project deps — if `python -m pytest` fails with
  `ModuleNotFoundError`, `pip install` the deps above for the interpreter at
  `/usr/local/bin/python3` (check `python3 -c "import sys; print(sys.path)"`
  if confused about which interpreter/env is active).

## 4. How to run things

```bash
python -m pytest tests/ -v --tb=short     # run after EVERY change — project rule #8
```

Current test files: `test_schemas.py`, `test_aero_avl.py`,
`test_aero_avl_builder.py`, `test_aero_xfoil.py`, `test_aero_su2_transonic.py`,
`test_propulsion_inlet.py`, `test_missions_staged.py`.

```bash
# Each analysis script writes a JSON + PNG next to itself when run directly
python3 analyses/stability/barrowman_stability.py
python3 analyses/trajectory/booster_burnout.py
python3 analyses/propulsion/inlet_performance.py
python3 workflows/ramp_staged_mission.py
```

Load a vehicle config:

```python
from src.schemas.vehicle_schema import BaseVehicleConfig
cfg = BaseVehicleConfig.from_yaml("vehicles/ramjet_rocket/vehicle_config.yaml")
# dispatches on vehicle_type -> UAVConfig | RocketConfig
```

---

## 5. Architecture & extension rules (must follow — see CLAUDE.md for full text)

1. **Never rewrite `core/` or `trunk/SUAVE/`.** Extend by subclassing
   `BaseAnalysis`/`BaseComponent`; return results as `AnalysisResults`.
2. **SI units always**, encoded in field names (`thrust_N`, `span_m`, `isp_s`).
3. **Type hints** on all public functions; **Google-style docstrings**
   (English) with a theory reference for physics code.
4. Every new file starts with: `# MELprop-IADE | <module.path> | v0.1.0`.
5. **Method applicability:** AVL only for Mach < 0.6 and |alpha| < 15 degrees;
   above that use empirical correlations. Never AVL for the supersonic ramP
   cruise.
6. `# TBD` / `# SZACOWANY` in YAML/comments = placeholder needing real data —
   never present these as validated in a report or trust them for a real
   physical conclusion.
7. Fidelity ladder: L0 analytical/handbook, L1 linear (VLM/XFOIL/DATCOM),
   L2 Euler CFD / 1-D cycle, L3 RANS/FEM.
8. Config schema is Pydantic v2, `extra="forbid"` — new fields require
   editing **both** `src/schemas/vehicle_schema.py` **and**
   `tests/unit/test_schemas.py`.
9. When spawning subagents in parallel on a shared working tree: they write
   files only and do **not** run git; the orchestrator (you, if you're
   coordinating) commits.

---

## 6. Work completed and MERGED into `develop` (do not redo)

Two parallel lines of work both merged into `develop` today (2026-07-08):

- **PR #11** (branch `claude/melprop-iade-infrastructure-e5b2cn`, this
  session) — merged 21:42 UTC.
- **PR #10** (branch `claude/melprop-iade-infrastructure-rcqzfg`, a different
  concurrent session) — merged 23:10 CEST/21:10 UTC, added only this file
  (`doc/AGENT_CONTEXT.md`, now rewritten) and a `CLAUDE.md` pointer to it — no
  code changes.

`develop` HEAD as of writing: `6759fdb4` ("Merge pull request #11 ...").

### Delivered in PR #11 (verified, 62/66 tests passing at merge time — see §7 for the other 4)

1. **Stage-1 thrust peak/mean inconsistency — RESOLVED.**
   `SolidRocketPropulsion` (`src/schemas/vehicle_schema.py`) now has an
   explicit `thrust_mean_N` field (was only a derived property) alongside
   `thrust_peak_N`, with validators: peak >= mean always, and mean
   cross-checked against `Isp_sl*mdot*g0` within 2x. Previously the YAML
   listed `thrust_peak_N: 12000` with an impulse-consistent mean of ~25.4 kN
   — a peak below the mean is physically impossible. Now
   `thrust_peak_N: 29000`, `thrust_mean_N: 25375` (both still `SZACOWANY` —
   not a real datasheet; the R-13 in Fusion is a geometry mockup only).
2. **0-degree horizontal launch — RESOLVED.**
   `analyses/trajectory/booster_burnout.py` previously launched flat (0
   degrees) with no lift and hit the ground at t~4.53s, before the nominal 6s
   burnout. `LAUNCH_ANGLE_DEG` is now 83 degrees (near-vertical rail launch)
   with a zero-lift gravity-turn approximation. Booster now survives to
   nominal burnout: Mach 1.23, altitude 1289 m, velocity 413.5 m/s at
   burnout. This is a first-order fix (3-DOF point-mass, no real autopilot) —
   good enough to unblock the staged mission, not flight-software-grade.
3. **Staged mission — implemented.** New `workflows/ramp_staged_mission.py`
   builds a 3-segment mission via `core/mission_builder.py`'s
   `MissionBuilder`: `boost_stage_1` -> `staging_event` (booster burnout
   state fed forward as the next segment's initial conditions) ->
   `cruise_stage_2_ramjet`. **The cruise segment itself is a documented
   placeholder/stub** (fixed duration/altitude/fuel guesses, not a real
   ramjet-cruise ODE integration) — if you need real cruise performance,
   that's still open work.
4. **GTM-140 (Project A) real datasheet values — partially resolved.**
   Sourced via web search from a peer-reviewed paper (DOI
   10.1515/eng-2015-0053): thrust 140 N (confirms the old placeholder was
   already right), mass flow 0.35 kg/s, compression ratio 2.8:1, EGT 700 degC
   (973.15 K), diameter 110 mm, length 265 mm, max RPM 120,000. Added as new
   *optional* fields on `TurbojetConfig`. **Still TBD, deliberately not
   fabricated:** `mass_kg`, `sfc_kg_per_Ns` (no reliable GTM-140-specific
   source found — don't reuse the "1.2 kg / 100N-thrust engine" number
   floating around some papers, that's a different engine class), and
   `wing.aspect_ratio` (this is the team's own airframe design, not a
   published engine spec — nothing to source from the web, needs the team's
   own CAD/design data).
5. **Ixx/Iyy/Izz moments of inertia — confirmed un-automatable, documented.**
   Fusion 360 only exposes the inertia tensor via its GUI Physical Properties
   panel, not its scripting API. `vehicles/ramjet_rocket/vehicle_config.yaml`'s
   `tbd:` list has precise manual-extraction instructions (which panel, which
   units). **Do not** approximate this with a simplified mass model (e.g.
   cylinder + point masses) as a substitute for the real CAD-derived tensor —
   that would misrepresent a placeholder as real data (rule #6 above). This
   needs a human with Fusion 360 open, full stop.
6. **Aero stubs implemented** (all previously empty scaffolds):
   - `analyses/aero/xfoil_runner.py`: Ackeret linearized supersonic theory at
     the M2.5 design point; XFOIL subprocess path (guarded) with analytical
     flat-plate fallback for the subsonic boost-initiation/recovery regime.
   - `analyses/aero/avl_builder.py`: AVL deck generator for the **ramP fins**,
     restricted to the low-speed boost-initiation/recovery envelope only
     (Mach < 0.6 enforced) — this is intentionally not for Project A and not
     for the supersonic cruise.
   - `analyses/aerodynamics/avl_wrapper.py`: AVL subprocess wired end-to-end
     for the **Project A (GTM-140) wing**, `helmbold_cl_alpha` analytical
     fallback kept and still what actually executes (no `avl` binary here).
   - `analyses/cfd/su2_config_template.py`: Mach-sweep `.cfg` generation plus
     a supersonic-linearized-theory CP estimate that cross-checks
     `analyses/stability/barrowman_stability.py`'s transonic CP bridge.
     **Finding:** Barrowman and the independent linearized estimate agree
     within ~6% at Mach 2.0 (validates the supersonic regime). The Mach~1
     linear-bridge region itself is still **not** validated by any
     closed-form theory or real CFD run — flagged as an open question in
     `doc/ramP/analysis_status.md`, not silently trusted.

---

## 7. NOT done / IN PROGRESS — read carefully before touching `analyses/propulsion/`

**Ramjet inlet redesign for MIL-E-5007 (task: redesign the single conical
spike as a multi-cone external-compression inlet).** This is genuinely
unfinished. It does NOT exist in any commit or PR — it is parked in a **git
stash** in this container (working tree was left red with 4 failing tests,
which can't be committed per the "never commit red tests" rule, so it was
stashed instead of discarded):

```
stash@{0}: "WIP: multi-cone inlet redesign (4/4 failing tests need n_cones 2/3->4, see doc/AGENT_CONTEXT.md sec 7)"
  analyses/propulsion/inlet_performance.py (+528 lines vs merged develop)
  tests/unit/test_propulsion_inlet.py (+159 lines)
```

If you are continuing in this same container: `git stash list` to confirm
it's still there, `git stash show -p stash@{0}` to inspect it, `git stash
pop` to restore it into the working tree before resuming — do not discard it
(`git stash drop` or ignoring it) without reading it first, it's real,
mostly-good work. If you are a fresh session in a different
environment/clone, this stash does not exist for you (stashes are local to
this one working directory and were never pushed) — this whole section is
then just a description of the physics/design work still to do, re-derivable
from the table and bug list below, not a file to go find.

**Current test status with this WIP applied:** 62 passed, 4 failed (all 4 in
`tests/unit/test_propulsion_inlet.py`). Without it (i.e. at merged `develop`
HEAD), the single-cone-only `inlet_performance.py` has 45 passing tests, all
green.

**What the WIP already built (functionally solid):**
- `multi_cone_recovery_chain(mach1, theta_rad_sequence, eta_diffuser)`:
  generalizes the existing single-cone `inlet_recovery_chain` to N sequential
  oblique shocks + a terminal normal shock + diffuser efficiency. Keeps the
  original single-cone function intact/untouched (still the as-built,
  Fusion-verified baseline).
- `optimize_multi_cone_angles(mach_design, n_cones, eta_diffuser)`: SLSQP
  optimizer over the N deflection angles, maximizing `eta_inlet` subject to
  all shocks staying attached. **This part works correctly** — independently
  verified by hand (see below).
- `MultiConeInletPerformanceAnalysis(BaseAnalysis)`: wraps the above as an
  analysis, alongside the original single-cone `InletPerformanceAnalysis`
  (both are meant to stay queryable — single-cone is the as-built Fusion
  geometry, multi-cone is explicitly tagged
  `geometry_status: redesign_proposal_not_yet_in_fusion` since a compound
  multi-cone spike doesn't match the existing Fusion CAD and would need a
  model update if adopted).

**The actual bug / gap, precisely:**
1. Manually re-running `optimize_multi_cone_angles(2.5, n_cones=N)` for
   N=2..7 gives:
   | N cones | eta_inlet | margin vs MIL-E-5007 (0.8703) | passes? |
   |---|---|---|---|
   | 2 | 0.7984 | -0.0720 | NO |
   | 3 | 0.8487 | -0.0216 | NO |
   | 4 | 0.8741 | +0.0037 | **yes** (thin margin) |
   | 5 | 0.8883 | +0.0179 | yes |
   | 6 | 0.8969 | +0.0265 | yes |
   | 7 | 0.9024 | +0.0321 | yes |

   So **2 and 3 cones cannot physically meet MIL-E-5007 at Mach 2.5 — this
   is a correct physics finding, not a bug** (the WIP's own code comments,
   citing Seddon & Goldsmith "Intake Aerodynamics" 1999 Sec 4.3, already say
   "4+ cones are required"). A constant `MULTI_CONE_THETA_DEG_4CONE = (9, 9,
   9, 9)` (equal-angle) preset was added and gives eta_inlet=0.8724, just
   barely over the 0.8703 threshold — workable but thin; 5 cones (7 deg each)
   gives more comfortable margin (0.8883).
2. **Four tests still assert a 2-cone or 3-cone design passes
   MIL-E-5007** — that's the actual defect, a test/expectation bug, not a
   physics bug: `test_optimize_multi_cone_angles_2cone_meets_mil_e_5007`,
   `test_optimize_multi_cone_angles_3cone_meets_mil_e_5007`,
   `test_multi_cone_inlet_analysis_design_point_meets_mil_e_5007` (uses
   `n_cones=2`), `test_multi_cone_inlet_analysis_3cone_design` (uses
   `n_cones=3`). These need to be changed to target 4 or more cones (and
   probably renamed to match, e.g. `..._4cone_...`), not have the underlying
   physics fudged to pass a wrong expectation.
3. **A real bug found but not yet fixed**: `MultiConeInletPerformanceAnalysis`
   defaults to `n_cones=2` in both `__init__` (line ~899) and `setup()`'s
   default parameter (line ~909) — should default to 4 (or reference
   `DEFAULT_N_CONES_M25`, which is already defined as 4 at module level but
   unused by the class defaults). Also, `setup(..., optimize_angles=False)`
   with `n_cones in {2, 3}` calls into `MULTI_CONE_THETA_DEG_2CONE` /
   `MULTI_CONE_THETA_DEG_3CONE` module constants that **do not exist**
   anywhere in the file (only `_4CONE` and `_5CONE` are defined) — this would
   raise `NameError` if that code path is ever exercised. No current test
   hits it (all tests use `optimize_angles=True`), but it's a live landmine
   for the next person who calls `setup(optimize_angles=False, n_cones=2)`.

**To finish this task:** bump the class default to 4 cones, delete or fix
the dead `_2CONE`/`_3CONE` constant references (either define them properly
for a documented reason, or simplify the `else` branch to always optimize for
non-4/5 presets), update the 4 failing tests to target a cone count that
actually clears MIL-E-5007 (4 minimum, 5 for comfortable margin), rerun
`python -m pytest tests/ -v --tb=short` and confirm fully green, then hand to
the orchestrator to commit (subagents don't run git themselves per §5 rule 9).

---

## 8. Other known caveats / open questions (carried over, still true)

- **Barrowman static margin looks over-stable.** CP 4.128 m, SM 10.08
  calibers — typical safe range is 1-2 calibers. The fin set is very large
  (span 2.67x body diameter) — worth checking whether that's an intentional
  design choice or a geometry artifact before trusting the margin number at
  face value.
- **Nozzle** in the Fusion geometry is currently modeled with
  `nozzle_area_ratio: 4.0` in the YAML (a design intent value) but the actual
  Fusion CAD nozzle may still be a simple cylindrical stub geometrically —
  worth double-checking against the CAD if you touch the ramjet cycle;
  no full ramjet combustor+nozzle cycle model exists yet (inlet only).
- **`doc/ramP/preliminary_analysis_report.md` is STALE** — written before
  this session's fixes, still shows old numbers (0.661 inlet eta,
  pre-fix trajectory, etc.). Don't cite it as current; `doc/ramP/analysis_status.md`
  is the maintained live tracker and is current as of this update.
- **Config reconciliation note** (carried from before this session): the
  schema-validated `vehicle_config.yaml` (with SZACOWANY estimates) was
  deliberately chosen over an alternative authoritative Fusion export with
  `null` propulsion fields, per an earlier explicit user decision. The raw
  export is retained in `fusion_extraction_v6.yaml` for reference.

---

## 9. Subagents (`.claude/agents/`)

Delegate domain work to the matching subagent (each carries its own scope +
rules):

| Agent | Model | Scope |
|---|---|---|
| aero-analyst | claude-sonnet-4-5 | `analyses/aerodynamics/`, `analyses/aero/`, `analyses/cfd/`, `tests/test_aero_*` |
| propulsion-designer | claude-opus-4-5 | `analyses/propulsion/`, `tests/test_propulsion_*` |
| vehicle-builder | claude-sonnet-4-5 | `src/schemas/`, `vehicles/**`, `tests/test_schemas.py` |
| mission-planner | claude-sonnet-4-5 | `workflows/`, `analyses/trajectory/`, `tests/test_missions_*` |
| code-reviewer | claude-haiku-4-5 | read-only everywhere, write only `tests/` |
| docs-writer | claude-haiku-4-5 | `notebooks/`, `*.md` |

When running them in parallel on a shared working tree: they write files
only and do **not** run git; the orchestrating session commits (and should
avoid committing a subagent's work if it leaves the test suite red — see
§10 for exactly this situation encountered this session).

---

## 10. Git / PR workflow state — READ THIS BEFORE COMMITTING ANYTHING

- Default/base branch: `develop`. Current `develop` HEAD: `6759fdb4`.
- This session worked on `claude/melprop-iade-infrastructure-e5b2cn`, whose
  PR (**#11**) is **already merged** into `develop` (merged commit
  `6759fdb4`, at `a9375bd6`).
- **A different, concurrent session** worked on
  `claude/melprop-iade-infrastructure-rcqzfg`; its PR (**#10**, doc-only) is
  **also already merged** (merged commit `d4d8f40e`).
- The local clone in this container is on branch
  `claude/melprop-iade-infrastructure-e5b2cn`, currently at commit
  `65631dad` — **which is 3 commits behind current `origin/develop` and 2
  commits ahead of the point where PR #11 was merged** (`a9375bd6`). Those 2
  ahead-commits (`b2cc871d` "aero stubs", `65631dad` "handoff doc") are
  **real, tested, green work that was never included in PR #11** (PR #11 was
  merged by the user mid-session, only capturing the first 2 of this
  session's 4 commits) **and are not yet in any merged PR**.
- On top of all that, there is the **uncommitted** inlet-redesign WIP
  described in §7.
- **Per this project's own git workflow convention** (a branch whose PR is
  already merged should be restarted from the latest default branch, keeping
  any not-yet-merged commits by rebasing them onto the new base rather than
  discarding them): the correct next action, when someone resumes real work
  here, is roughly:
  1. Finish or deliberately drop the uncommitted §7 WIP (don't silently lose
     it — it has real, cited physics content).
  2. `git fetch origin develop`
  3. Rebase the 2 unmerged commits (`b2cc871d`, `65631dad`) onto
     `origin/develop`'s new tip (`6759fdb4`) — do not just hard-reset the
     branch to `origin/develop`, that would silently drop real work.
  4. Run `python -m pytest tests/ -v --tb=short`, confirm green.
  5. Push (force-with-lease, since history was rewritten) and open a **new**
     PR — do not try to reuse #11, it's closed/merged.
- No CI is configured on this repo (checked PR #11's combined status:
  `total_count: 0`) — "green" here means the local pytest run, not a GitHub
  check.

---

## 11. Suggested next steps (priority order, updated)

1. **Finish the multi-cone inlet redesign** (§7) — the physics is basically
   done, it's a cone-count/test-expectation fix, should be quick.
2. Resolve the git state in §10 (rebase, new PR) once #1 is settled.
3. Obtain the **real stage-1 motor datasheet** to replace the SZACOWANY
   thrust/Isp values (R-13 in Fusion is a geometry mockup only).
4. Real ramjet **combustor + nozzle cycle** model (inlet-only so far); wire
   into the `cruise_stage_2_ramjet` mission segment stub.
5. Source or measure GTM-140 `mass_kg`/`sfc_kg_per_Ns` and the drone's real
   `wing.aspect_ratio` (team CAD data, not public literature).
6. Get **Ixx/Iyy/Izz** from a human with Fusion 360 open (§6 item 5).
7. Sanity-check the Barrowman static-margin/fin-size finding (§8).

Keep `doc/ramP/analysis_status.md` updated as items move STUB/TBD -> DONE.
