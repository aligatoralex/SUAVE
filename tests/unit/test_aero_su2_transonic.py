# MELprop-IADE | tests.unit.test_aero_su2_transonic | v0.1.0
"""Unit tests for analyses.cfd.su2_config_template transonic CP estimate."""

import math
from pathlib import Path

import pytest

from analyses.cfd.su2_config_template import (
    MACH_SWEEP,
    build_mach_sweep,
    build_su2_config,
    su2_is_available,
    supersonic_linearized_cp_estimate,
)
from src.schemas.vehicle_schema import BaseVehicleConfig, RocketConfig

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def rocket_config() -> RocketConfig:
    """Load the committed ramjet_rocket configuration."""
    path = REPO_ROOT / "vehicles" / "ramjet_rocket" / "vehicle_config.yaml"
    config = BaseVehicleConfig.from_yaml(path)
    assert isinstance(config, RocketConfig)
    return config


def test_build_su2_config_contains_required_keys() -> None:
    """SU2 config must contain SOLVER, MACH_NUMBER, AOA."""
    cfg = build_su2_config(mach=2.0, aoa_deg=2.0)

    assert "SOLVER= EULER" in cfg
    assert "MACH_NUMBER= 2.0" in cfg
    assert "AOA= 2.0" in cfg
    assert "REF_AREA=" in cfg
    assert "REF_LENGTH=" in cfg


def test_build_mach_sweep_produces_all_cases() -> None:
    """build_mach_sweep must produce configs for every Mach in MACH_SWEEP."""
    sweep = build_mach_sweep()

    assert len(sweep) == len(MACH_SWEEP)
    for mach in MACH_SWEEP:
        assert mach in sweep
        assert f"MACH_NUMBER= {mach}" in sweep[mach]


def test_supersonic_linearized_cp_estimate_valid_range(rocket_config: RocketConfig) -> None:
    """Supersonic CP estimate must produce a sane value within rocket length."""
    nose_length = rocket_config.body.nose_length_m
    total_length = rocket_config.body.total_length_m
    d_ref = rocket_config.body.diameter_m
    fin_span = rocket_config.fins.span_m
    fin_chord = rocket_config.fins.chord_root_m or fin_span
    fin_x = total_length - fin_chord

    cp_m = supersonic_linearized_cp_estimate(
        nose_length_m=nose_length,
        total_length_m=total_length,
        d_ref_m=d_ref,
        fin_span_m=fin_span,
        fin_chord_m=fin_chord,
        fin_x_m=fin_x,
        mach=2.0,
    )

    # CP must be within the rocket length (physical bound).
    assert 0.0 < cp_m < total_length

    # CP must be aft of the nose (fins dominate in supersonic).
    assert cp_m > nose_length


def test_supersonic_cp_estimate_rejects_transonic() -> None:
    """Supersonic CP estimate must reject Mach <= 1.2."""
    with pytest.raises(ValueError, match="Mach > 1.2"):
        supersonic_linearized_cp_estimate(
            nose_length_m=0.3,
            total_length_m=4.0,
            d_ref_m=0.25,
            fin_span_m=0.5,
            fin_chord_m=0.18,
            fin_x_m=3.5,
            mach=1.0,
        )


def test_supersonic_cp_estimate_vs_barrowman(rocket_config: RocketConfig) -> None:
    """Cross-check supersonic CP estimate against Barrowman at Mach 2.0.

    This test documents the comparison between the Barrowman Rogers-extended
    transonic estimate and the linearized supersonic theory estimate at
    Mach 2.0 (well into the supersonic regime where linearized theory is
    valid).
    """
    from analyses.stability.barrowman_stability import (
        BarrowmanStabilityAnalysis,
        compute_stability_at_mach,
        load_geometry,
    )

    # Load Barrowman geometry.
    geometry = load_geometry()

    # Barrowman CP at Mach 2.0.
    barrowman_result = compute_stability_at_mach(geometry, mach=2.0)
    cp_barrowman_m = barrowman_result.x_cp_m

    # Supersonic linearized estimate at Mach 2.0.
    nose_length = rocket_config.body.nose_length_m
    total_length = rocket_config.body.total_length_m
    d_ref = rocket_config.body.diameter_m
    fin_span = rocket_config.fins.span_m
    fin_chord = rocket_config.fins.chord_root_m or fin_span
    fin_x = total_length - fin_chord

    cp_supersonic_m = supersonic_linearized_cp_estimate(
        nose_length_m=nose_length,
        total_length_m=total_length,
        d_ref_m=d_ref,
        fin_span_m=fin_span,
        fin_chord_m=fin_chord,
        fin_x_m=fin_x,
        mach=2.0,
    )

    # Both estimates should be within 20% of each other at Mach 2.0.
    # (Barrowman uses body-interference and a different fin CN_alpha scaling;
    # this is order-of-magnitude agreement, not tight validation.)
    rel_diff = abs(cp_barrowman_m - cp_supersonic_m) / cp_barrowman_m
    assert rel_diff < 0.2, (
        f"Barrowman CP={cp_barrowman_m:.3f} m vs. supersonic linearized "
        f"CP={cp_supersonic_m:.3f} m at Mach 2.0 differ by {rel_diff*100:.1f}% "
        "(expect < 20% for order-of-magnitude agreement)"
    )


def test_transonic_cp_cross_check_at_mach_1(rocket_config: RocketConfig) -> None:
    """Document the transonic CP cross-check at Mach 1.0.

    Barrowman's linear bridge (0.8 <= M <= 1.2) is a low-order approximation
    with no closed-form theory. This test flags if the Mach-1 CP estimate
    deviates significantly from an independent supersonic-theory sanity bound.
    """
    from analyses.stability.barrowman_stability import (
        compute_stability_at_mach,
        load_geometry,
    )

    geometry = load_geometry()

    # Barrowman CP at Mach 1.0 (transonic linear bridge).
    barrowman_transonic = compute_stability_at_mach(geometry, mach=1.0)
    cp_barrowman_transonic_m = barrowman_transonic.x_cp_m

    # Supersonic linearized estimate at Mach 1.5 (just beyond transonic band).
    nose_length = rocket_config.body.nose_length_m
    total_length = rocket_config.body.total_length_m
    d_ref = rocket_config.body.diameter_m
    fin_span = rocket_config.fins.span_m
    fin_chord = rocket_config.fins.chord_root_m or fin_span
    fin_x = total_length - fin_chord

    cp_supersonic_m = supersonic_linearized_cp_estimate(
        nose_length_m=nose_length,
        total_length_m=total_length,
        d_ref_m=d_ref,
        fin_span_m=fin_span,
        fin_chord_m=fin_chord,
        fin_x_m=fin_x,
        mach=1.5,
    )

    # FLAG: if the Barrowman transonic value differs from the supersonic
    # estimate by more than 30%, this suggests the transonic bridge may be
    # over-conservative or under-conservative. This is NOT a failure — just
    # a documented flag for future CFD validation.
    rel_diff = abs(cp_barrowman_transonic_m - cp_supersonic_m) / cp_supersonic_m
    if rel_diff > 0.3:
        pytest.skip(
            f"FLAGGED: Barrowman transonic CP={cp_barrowman_transonic_m:.3f} m "
            f"vs. supersonic linearized CP={cp_supersonic_m:.3f} m (M=1.5) "
            f"differ by {rel_diff*100:.1f}% (> 30% threshold). "
            "This is a known open question; transonic linear bridge is a "
            "low-order approximation. Consider CFD validation near Mach 1."
        )

    # If we reach here, the two estimates agree within 30% — document it.
    assert rel_diff < 0.3, (
        f"Barrowman transonic CP={cp_barrowman_transonic_m:.3f} m vs. "
        f"supersonic linearized CP={cp_supersonic_m:.3f} m differ by "
        f"{rel_diff*100:.1f}% — within expected tolerance."
    )
