# MELprop-IADE | tests.unit.test_aero_xfoil | v0.1.0
"""Unit tests for analyses.aero.xfoil_runner."""

import math

import pytest

from analyses.aero.xfoil_runner import (
    FIN_CHORD_M,
    FIN_DESIGN_MACH,
    FIN_THICKNESS_MAX_M,
    XfoilCase,
    XfoilRunner,
    double_wedge_coordinates,
    supersonic_double_wedge_polar,
    xfoil_is_available,
)
from core.component_base import FidelityLevel


def test_double_wedge_coordinates_symmetry() -> None:
    """Double-wedge coordinates must be symmetric about the x-axis."""
    t_c = FIN_THICKNESS_MAX_M / FIN_CHORD_M
    coords = double_wedge_coordinates(t_c, n_points=10)

    # First coord is TE at (1, 0).
    assert coords[0] == (1.0, 0.0)

    # Total number: 1 (TE) + 10 (upper) + 10 (lower) = 21.
    assert len(coords) == 21

    # Check y-symmetry: upper[i].y == -lower[i].y.
    upper_y = [coords[i][1] for i in range(1, 11)]
    lower_y = [coords[i][1] for i in range(11, 21)]
    for yu, yl in zip(upper_y, lower_y[::-1]):
        assert yu == pytest.approx(-yl, abs=1e-6)


def test_supersonic_double_wedge_polar_valid_range() -> None:
    """Supersonic polar must produce sane CL, CD, CM at Mach 2.5."""
    t_c = FIN_THICKNESS_MAX_M / FIN_CHORD_M
    cl, cd, cm = supersonic_double_wedge_polar(t_c, mach=2.5, alpha_deg=4.0)

    # CL > 0 for positive alpha.
    assert cl > 0.0
    # CD > 0 (wave drag dominates).
    assert cd > 0.0
    # CM = 0 for symmetric section.
    assert cm == pytest.approx(0.0, abs=1e-9)
    # CL_alpha ~ 4 / sqrt(M^2 - 1) ~ 1.7 at M=2.5.
    alpha_rad = math.radians(4.0)
    expected_cl = 4.0 / math.sqrt(2.5**2 - 1.0) * alpha_rad
    assert cl == pytest.approx(expected_cl, rel=0.01)


def test_supersonic_polar_rejects_transonic() -> None:
    """Supersonic polar must reject Mach <= 1.2."""
    t_c = FIN_THICKNESS_MAX_M / FIN_CHORD_M
    with pytest.raises(ValueError, match="Mach > 1.2"):
        supersonic_double_wedge_polar(t_c, mach=1.0, alpha_deg=0.0)


def test_xfoil_runner_supersonic() -> None:
    """XfoilRunner must use supersonic theory for M >= 2.5."""
    case = XfoilCase(reynolds=1e6, mach=FIN_DESIGN_MACH)
    runner = XfoilRunner()
    runner.setup(case)
    results = runner.execute()

    assert results.fidelity == FidelityLevel.LEVEL_1
    assert "CL_alpha" in results
    assert results["CL_alpha"] > 0.0
    assert results.metadata["method"] == "supersonic_linearized_ackeret_double_wedge"


def test_xfoil_runner_subsonic_analytical() -> None:
    """XfoilRunner must fall back to analytical for subsonic without xfoil binary."""
    case = XfoilCase(reynolds=5e5, mach=0.3)
    runner = XfoilRunner()
    runner.setup(case)
    results = runner.execute()

    assert results.fidelity == FidelityLevel.LEVEL_1
    assert "CL_alpha" in results
    # Flat-plate CL_alpha ~ 2*pi / sqrt(1 - M^2) ~ 6.5 at M=0.3.
    expected_cl_alpha = 2.0 * math.pi / math.sqrt(1.0 - 0.3**2)
    assert results["CL_alpha"] == pytest.approx(expected_cl_alpha, rel=0.01)

    # Method must be analytical (xfoil binary not available in sandbox).
    if not xfoil_is_available():
        assert "analytical" in results.metadata["method"]


def test_xfoil_runner_execute_before_setup_raises() -> None:
    """execute() without setup() must raise RuntimeError."""
    with pytest.raises(RuntimeError, match="called before setup"):
        XfoilRunner().execute()
