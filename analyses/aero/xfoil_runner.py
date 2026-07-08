# MELprop-IADE | analyses.aero.xfoil_runner | v0.1.0
"""XFOIL batch-run for the stabilizer fin airfoil and supersonic polar.

The MELprop ramjet rocket uses rectangular steel fins with a maximum
thickness of 30 mm over a 176.8 mm chord (t/c ~ 0.17). At the cruise
design point the fins operate at Mach 2.5, where a sharp double-wedge
(diamond) section is preferred to minimise wave drag. XFOIL is a
low-speed (incompressible/weakly-compressible) panel + boundary-layer
code and is therefore only valid for the *subsonic* portions of the
flight envelope (boost initiation, recovery); the supersonic fin loads
must come from linearised supersonic theory or CFD (see
``analyses/cfd/su2_config_template.py``).

Theory reference:
    Ames Research Staff, "Equations, Tables, and Charts for Compressible
    Flow", NACA Report 1135 (1953) — supersonic wave-drag of thin
    sections. Drela, M., "XFOIL: An Analysis and Design System for Low
    Reynolds Number Airfoils", NACA TN 1428-style low-Re methodology.
"""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from core.component_base import AnalysisResults, BaseAnalysis, FidelityLevel

#: Fin section geometry (Fusion Assembly v6).
FIN_CHORD_M = 0.1768
FIN_THICKNESS_MAX_M = 0.030
FIN_DESIGN_MACH = 2.5


def xfoil_is_available() -> bool:
    """Return True if the ``xfoil`` executable is on ``PATH``."""
    return shutil.which("xfoil") is not None


def double_wedge_coordinates(thickness_to_chord: float, n_points: int = 50) -> list[tuple[float, float]]:
    """Generate coordinates for a symmetric double-wedge (diamond) airfoil.

    Args:
        thickness_to_chord: Section thickness ratio t/c (dimensionless).
        n_points: Number of points per surface (upper + lower).

    Returns:
        List of (x, y) coordinates, normalized to unit chord, starting from
        the trailing edge, proceeding forward over the upper surface to the
        leading edge, then aft over the lower surface back to the TE.
    """
    half_t = thickness_to_chord / 2.0
    upper = [(1.0 - i / (n_points - 1), half_t * i / (n_points - 1)) for i in range(n_points)]
    lower = [(i / (n_points - 1), -half_t * i / (n_points - 1)) for i in range(n_points)]
    # Close the loop: TE -> LE upper -> LE -> LE lower -> TE.
    coords = [(1.0, 0.0)] + upper[::-1] + lower
    return coords


def supersonic_double_wedge_polar(
    thickness_to_chord: float, mach: float, alpha_deg: float
) -> tuple[float, float, float]:
    """Supersonic linearized wave-drag theory for a symmetric double-wedge.

    Valid for Mach > 1.2, small alpha. Based on NACA Report 1135 (Ackeret
    thin-airfoil theory) with wave-drag from the section thickness.

    Args:
        thickness_to_chord: Section thickness ratio t/c.
        mach: Freestream Mach number (must be > 1.2).
        alpha_deg: Angle of attack in degrees.

    Returns:
        Tuple of (CL, CD, CM) for the section, referenced to chord.

    Raises:
        ValueError: If Mach <= 1.2 (transonic / subsonic regime invalid).
    """
    if mach <= 1.2:
        raise ValueError(
            f"supersonic_double_wedge_polar requires Mach > 1.2; got {mach}"
        )
    beta = math.sqrt(mach**2 - 1.0)
    alpha_rad = math.radians(alpha_deg)

    # Ackeret thin-airfoil lift (2D section): CL = 4 * alpha / sqrt(M^2 - 1).
    cl = 4.0 * alpha_rad / beta

    # Wave drag: CD_wave = (4 / beta) * (t/c)^2 for a double-wedge.
    # Plus induced drag from lift: CD_induced = CL * alpha (linearized).
    cd_wave = 4.0 * (thickness_to_chord**2) / beta
    cd_induced = cl * alpha_rad
    cd = cd_wave + cd_induced

    # Symmetric section: CM = 0 at the quarter-chord.
    cm = 0.0

    return cl, cd, cm


@dataclass
class XfoilCase:
    """Single XFOIL run specification.

    Attributes:
        reynolds: Chord Reynolds number.
        mach: Freestream Mach number (XFOIL valid only for M < ~0.7).
        alpha_deg_range: (start, stop, step) angle-of-attack sweep [deg].
    """

    reynolds: float
    mach: float
    alpha_deg_range: tuple[float, float, float] = (-6.0, 12.0, 1.0)
    extra_commands: list[str] = field(default_factory=list)


class XfoilRunner(BaseAnalysis):
    """XFOIL driver for the fin airfoil polar (subsonic + supersonic fallback).

    For subsonic conditions (Mach < 0.7), invokes XFOIL via subprocess when
    the binary is available; otherwise uses a flat-plate analytical estimate.
    For supersonic conditions (Mach >= 2.5), uses linearized supersonic
    theory (double-wedge wave-drag) from NACA Report 1135.

    Example:
        >>> case_subsonic = XfoilCase(reynolds=5e5, mach=0.3)
        >>> runner = XfoilRunner()
        >>> runner.setup(case_subsonic)
        >>> results = runner.execute()
        >>> results["CL_alpha"]  # doctest: +SKIP
    """

    fidelity = FidelityLevel.LEVEL_1

    def __init__(self, name: str = "xfoil_fin_polar") -> None:
        super().__init__(name)
        self._case: XfoilCase | None = None

    def setup(self, case: XfoilCase) -> None:
        """Bind a run case.

        Args:
            case: XFOIL case specification.
        """
        self._case = case
        self._is_setup = True

    def execute(self) -> AnalysisResults:
        """Run XFOIL (if available) or analytical fallback, and return the polar.

        Returns:
            AnalysisResults with ``CL``, ``CD``, ``CM``, ``CL_alpha`` [1/rad].

        Raises:
            RuntimeError: If called before :meth:`setup`.
        """
        if not self._is_setup or self._case is None:
            raise RuntimeError("XfoilRunner.execute() called before setup()")

        # Supersonic regime: use linearized theory.
        if self._case.mach >= 2.5:
            return self._execute_supersonic()

        # Subsonic regime: XFOIL subprocess if available, else flat-plate.
        if xfoil_is_available():
            method = "xfoil_subprocess"
            try:
                return self._execute_xfoil()
            except Exception as exc:
                # XFOIL can fail to converge; fall back to analytical.
                method = f"analytical_flat_plate (XFOIL failed: {exc})"
        else:
            method = "analytical_flat_plate"

        return self._execute_subsonic_analytical(method)

    def _execute_supersonic(self) -> AnalysisResults:
        """Supersonic double-wedge polar from linearized theory (M >= 2.5)."""
        assert self._case is not None
        alpha_start, alpha_stop, alpha_step = self._case.alpha_deg_range
        alpha_mid = (alpha_start + alpha_stop) / 2.0

        t_c = FIN_THICKNESS_MAX_M / FIN_CHORD_M
        cl, cd, cm = supersonic_double_wedge_polar(t_c, self._case.mach, alpha_mid)

        # CL_alpha from thin-airfoil theory: 4 / sqrt(M^2 - 1).
        beta = math.sqrt(self._case.mach**2 - 1.0)
        cl_alpha = 4.0 / beta

        return AnalysisResults(
            name=self.name,
            fidelity=self.fidelity,
            data={
                "CL": cl,
                "CD": cd,
                "CM": cm,
                "CL_alpha": cl_alpha,
            },
            metadata={
                "method": "supersonic_linearized_ackeret_double_wedge",
                "mach": self._case.mach,
                "alpha_deg": alpha_mid,
                "thickness_to_chord": t_c,
                "theory_reference": "NACA Report 1135 (1953)",
            },
        )

    def _execute_xfoil(self) -> AnalysisResults:
        """Drive XFOIL via subprocess for subsonic conditions."""
        assert self._case is not None
        t_c = FIN_THICKNESS_MAX_M / FIN_CHORD_M
        coords = double_wedge_coordinates(t_c, n_points=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            coord_file = tmppath / "wedge.dat"
            polar_file = tmppath / "polar.txt"

            # Write airfoil coordinates.
            with coord_file.open("w") as fh:
                fh.write("Double-wedge\n")
                for x, y in coords:
                    fh.write(f"{x:.6f} {y:.6f}\n")

            # Build XFOIL command script.
            alpha_start, alpha_stop, alpha_step = self._case.alpha_deg_range
            commands = [
                f"LOAD {coord_file}",
                "",  # airfoil name prompt
                "OPER",
                f"VISC {self._case.reynolds}",
                f"MACH {self._case.mach}",
                "PACC",
                f"{polar_file}",
                "",  # no dump file
                f"ASEQ {alpha_start} {alpha_stop} {alpha_step}",
                "",  # exit OPER
                "QUIT",
            ]
            commands_str = "\n".join(commands)

            # Run XFOIL.
            proc = subprocess.run(
                ["xfoil"],
                input=commands_str,
                text=True,
                capture_output=True,
                cwd=tmppath,
                timeout=30,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"XFOIL failed: {proc.stderr}")

            # Parse polar file.
            if not polar_file.exists():
                raise RuntimeError("XFOIL did not produce a polar file")

            cl_values, cd_values, cm_values = [], [], []
            with polar_file.open("r") as fh:
                for line in fh:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    parts = stripped.split()
                    if len(parts) >= 3:
                        try:
                            cl_values.append(float(parts[1]))
                            cd_values.append(float(parts[2]))
                            cm_values.append(float(parts[4]) if len(parts) > 4 else 0.0)
                        except (ValueError, IndexError):
                            pass

            if not cl_values:
                raise RuntimeError("XFOIL polar is empty")

            cl_avg = sum(cl_values) / len(cl_values)
            cd_avg = sum(cd_values) / len(cd_values)
            cm_avg = sum(cm_values) / len(cm_values)

            # Estimate CL_alpha from the polar slope (linear fit).
            alpha_vals = [
                alpha_start + i * alpha_step for i in range(len(cl_values))
            ]
            if len(alpha_vals) > 1:
                d_cl = cl_values[-1] - cl_values[0]
                d_alpha_rad = math.radians(alpha_vals[-1] - alpha_vals[0])
                cl_alpha = d_cl / d_alpha_rad if d_alpha_rad > 0 else 2.0 * math.pi
            else:
                cl_alpha = 2.0 * math.pi  # fallback

            return AnalysisResults(
                name=self.name,
                fidelity=self.fidelity,
                data={
                    "CL": cl_avg,
                    "CD": cd_avg,
                    "CM": cm_avg,
                    "CL_alpha": cl_alpha,
                },
                metadata={
                    "method": "xfoil_subprocess",
                    "mach": self._case.mach,
                    "reynolds": self._case.reynolds,
                    "alpha_range_deg": self._case.alpha_deg_range,
                    "n_converged": len(cl_values),
                },
            )

    def _execute_subsonic_analytical(self, method: str) -> AnalysisResults:
        """Subsonic flat-plate analytical fallback (thin-airfoil theory)."""
        assert self._case is not None
        alpha_start, alpha_stop, _ = self._case.alpha_deg_range
        alpha_mid = (alpha_start + alpha_stop) / 2.0
        alpha_rad = math.radians(alpha_mid)

        # Thin-airfoil theory: CL_alpha = 2*pi (incompressible).
        # Prandtl-Glauert correction for compressibility.
        beta = math.sqrt(1.0 - self._case.mach**2) if self._case.mach < 1.0 else 1.0
        cl_alpha = 2.0 * math.pi / beta
        cl = cl_alpha * alpha_rad

        # Flat-plate CD estimate: CD0 ~ 0.01 + CL^2 / (pi * AR_effective).
        # For a 2D section (infinite AR), just use a small viscous drag.
        cd = 0.01 + abs(cl * alpha_rad)

        # Symmetric section: CM = 0 at quarter-chord.
        cm = 0.0

        return AnalysisResults(
            name=self.name,
            fidelity=self.fidelity,
            data={
                "CL": cl,
                "CD": cd,
                "CM": cm,
                "CL_alpha": cl_alpha,
            },
            metadata={
                "method": method,
                "mach": self._case.mach,
                "reynolds": self._case.reynolds,
                "alpha_deg": alpha_mid,
            },
        )
