# MELprop-IADE | analyses.cfd.su2_config_template | v0.1.0
"""SU2 external-aerodynamics configuration-template and transonic CP estimate.

Generates SU2 ``.cfg`` files for an inviscid/RANS Mach sweep of the
ramjet rocket to extract CL/CD across the transonic–supersonic envelope,
complementing the low-order Barrowman (stability) and DATCOM-style drag
estimates used elsewhere in the project.

When SU2_CFD is not available, provides a lower-order supersonic-linearized
estimate of the center-of-pressure for cross-checking the Barrowman
transonic linear-bridge assumption (0.8 <= Mach <= 1.2).

Workflow (to be implemented):
    1. Mesh generation with gmsh from the axisymmetric body + fins.
    2. SU2_CFD run per Mach number (Euler first, then RANS/SA).
    3. Force-coefficient extraction (CL, CD, Cm) from the SU2 history.

Theory / tooling reference:
    Economon, T. D. et al., "SU2: An Open-Source Suite for Multiphysics
    Simulation and Design", AIAA Journal 54(3), 2016.
    Slender-body theory (Van Dyke, "Perturbation Methods in Fluid Mechanics")
    for body CN_alpha. Ackeret linearized supersonic theory for fins.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

#: Mach numbers swept for the external-aero study.
MACH_SWEEP: tuple[float, ...] = (0.8, 1.2, 1.5, 2.0, 2.5, 3.0)

#: SU2 config keys common to every Mach case (template defaults).
_BASE_CONFIG: dict[str, str] = {
    "SOLVER": "EULER",
    "MATH_PROBLEM": "DIRECT",
    "REF_DIMENSIONALIZATION": "DIMENSIONAL",
    "MARKER_EULER": "( airframe )",
    "MARKER_FAR": "( farfield )",
    "CONV_NUM_METHOD_FLOW": "JST",
    "ITER": "5000",
}


def su2_is_available() -> bool:
    """Return True if the ``SU2_CFD`` executable is on ``PATH``."""
    return shutil.which("SU2_CFD") is not None


def build_su2_config(mach: float, aoa_deg: float = 0.0) -> str:
    """Render an SU2 ``.cfg`` text for one Mach/AoA case.

    Args:
        mach: Freestream Mach number.
        aoa_deg: Angle of attack in degrees.

    Returns:
        SU2 configuration file contents as a string.

    Note:
        Stub: farfield pressure/temperature and reference area/length are
        placeholders and MUST be set from the vehicle config and ISA
        conditions before use (see module ``TODO``).
    """
    lines = [f"% SU2 case  Mach={mach}  AoA={aoa_deg} deg  (MELprop ramP)"]
    lines += [f"{k}= {v}" for k, v in _BASE_CONFIG.items()]
    lines += [
        f"MACH_NUMBER= {mach}",
        f"AOA= {aoa_deg}",
        "FREESTREAM_PRESSURE= 26500   % TODO: ISA at design altitude [Pa]",
        "FREESTREAM_TEMPERATURE= 223.3 % TODO: ISA at design altitude [K]",
        "REF_AREA= 0.04909            % pi/4 * 0.250^2 [m^2]",
        "REF_LENGTH= 0.250            % d_ref [m]",
        "MESH_FILENAME= ramp_airframe.su2  % TODO: gmsh output",
    ]
    return "\n".join(lines)


def build_mach_sweep() -> dict[float, str]:
    """Build SU2 configs for every Mach in :data:`MACH_SWEEP`.

    Returns:
        Mapping of Mach number to its SU2 ``.cfg`` text.
    """
    return {mach: build_su2_config(mach) for mach in MACH_SWEEP}


def supersonic_linearized_cp_estimate(
    nose_length_m: float,
    total_length_m: float,
    d_ref_m: float,
    fin_span_m: float,
    fin_chord_m: float,
    fin_x_m: float,
    mach: float,
) -> float:
    """Lower-order supersonic CP estimate from linearized slender-body theory.

    Supersonic (Mach > 1.2) CP estimate for a conical nose + cylindrical
    body + cruciform fins. Uses Van Dyke slender-body theory for the body
    (CN_alpha ~ 2 for a cone, CP at ~2/3 L_nose) and Ackeret thin-airfoil
    theory for the fins (CN_alpha ~ 4 / sqrt(M^2 - 1) per fin panel).

    Args:
        nose_length_m: Nose length [m].
        total_length_m: Total rocket length [m].
        d_ref_m: Reference body diameter [m].
        fin_span_m: Exposed fin semi-span [m].
        fin_chord_m: Fin root chord [m].
        fin_x_m: Axial position of fin root LE from nose [m].
        mach: Freestream Mach number (must be > 1.2).

    Returns:
        Combined CP location [m from nose tip].

    Raises:
        ValueError: If Mach <= 1.2 (transonic regime, theory invalid).
    """
    if mach <= 1.2:
        raise ValueError(
            "supersonic_linearized_cp_estimate requires Mach > 1.2; "
            f"got {mach} (transonic, theory invalid)"
        )

    beta = math.sqrt(mach**2 - 1.0)

    # Nose contribution: CN_alpha = 2 (referenced to nose base area),
    # scaled to body reference area.
    a_nose_base = math.pi / 4.0 * (d_ref_m * 0.6) ** 2  # assume nose base 0.6 * d_ref
    a_ref = math.pi / 4.0 * d_ref_m**2
    cn_nose = 2.0 * (a_nose_base / a_ref)
    x_cp_nose = 0.666 * nose_length_m  # cone CP at 2/3 L_nose

    # Fin contribution: 4 fins, Ackeret CN_alpha = 4 / beta per 2D section.
    # Planform area of one fin ~ span * chord; scale to reference area.
    s_fin = fin_span_m * fin_chord_m
    cn_fin_2d = 4.0 / beta
    # Cruciform body-interference factor (Hoerner-style): K_fb ~ 1 + R/(s+R).
    r_body = d_ref_m / 2.0
    k_fb = 1.0 + r_body / (fin_span_m + r_body)
    cn_fins_total = 4 * k_fb * cn_fin_2d * (s_fin / a_ref)
    x_cp_fins = fin_x_m + 0.5 * fin_chord_m  # mid-chord of fin

    # Combined CP via CN-weighted average.
    cn_total = cn_nose + cn_fins_total
    x_cp_combined = (cn_nose * x_cp_nose + cn_fins_total * x_cp_fins) / cn_total

    return x_cp_combined
