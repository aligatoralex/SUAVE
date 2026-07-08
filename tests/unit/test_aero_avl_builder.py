# MELprop-IADE | tests.unit.test_aero_avl_builder | v0.1.0
"""Unit tests for analyses.aero.avl_builder."""

import math
from pathlib import Path

import pytest

from analyses.aero.avl_builder import (
    AVLFinAnalysis,
    MAX_MACH,
    avl_is_available,
    build_avl_deck,
)
from core.component_base import FidelityLevel
from src.schemas.vehicle_schema import BaseVehicleConfig, RocketConfig

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def rocket_config() -> RocketConfig:
    """Load the committed ramjet_rocket configuration."""
    path = REPO_ROOT / "vehicles" / "ramjet_rocket" / "vehicle_config.yaml"
    config = BaseVehicleConfig.from_yaml(path)
    assert isinstance(config, RocketConfig)
    return config


def test_build_avl_deck_produces_valid_text(rocket_config: RocketConfig) -> None:
    """AVL deck must contain required header blocks and fin SURFACE."""
    deck = build_avl_deck(rocket_config, mach=0.3)

    assert "MELprop-Ramjet-Missile" in deck
    assert "#Mach" in deck
    assert "0.300" in deck
    assert "#Sref Cref Bref" in deck
    assert "SURFACE" in deck
    assert "Fins" in deck
    assert "SECTION" in deck


def test_avl_fin_analysis_rejects_high_mach(rocket_config: RocketConfig) -> None:
    """AVLFinAnalysis must reject Mach >= 0.6."""
    analysis = AVLFinAnalysis()
    with pytest.raises(ValueError, match="Mach"):
        analysis.setup(rocket_config, mach=0.8)


def test_avl_fin_analysis_analytical_fallback(rocket_config: RocketConfig) -> None:
    """AVLFinAnalysis must use Helmbold analytical when AVL binary unavailable."""
    analysis = AVLFinAnalysis()
    analysis.setup(rocket_config, mach=0.3)
    results = analysis.execute()

    assert results.fidelity == FidelityLevel.LEVEL_1
    assert "CL_alpha" in results
    assert "Cm_alpha" in results
    assert "neutral_point_m" in results

    # CL_alpha must be positive (fins add normal-force capability).
    assert results["CL_alpha"] > 0.0

    # Analytical method expected (AVL binary not available in sandbox).
    if not avl_is_available():
        assert "helmbold" in results.metadata["method"]


def test_avl_fin_analysis_execute_before_setup_raises() -> None:
    """execute() without setup() must raise RuntimeError."""
    with pytest.raises(RuntimeError, match="called before setup"):
        AVLFinAnalysis().execute()


def test_build_avl_deck_missing_geometry_raises(rocket_config: RocketConfig) -> None:
    """build_avl_deck must reject configs with diameter_m = 0."""
    # Manually modify a valid config to have invalid diameter (bypass Pydantic).
    rocket_config.body.diameter_m = 0.0

    with pytest.raises(ValueError, match="body.diameter_m must be > 0"):
        build_avl_deck(rocket_config, mach=0.3)
