# DroneEnv Workspace Summary

## Overview

This repository contains **SUAVE** (Stanford University Aerospace Vehicle Environment), an open-source multi-fidelity conceptual design environment for future aircraft incorporating advanced technologies. The framework is developed in Python and designed for credible conceptual-level design conclusions.

## Repository Structure

### Main Components

1. **`trunk/SUAVE/`** - Core SUAVE framework containing:
   - **Analyses**: Aerodynamics, Stability, Weights, Energy analysis modules
   - **Components**: Aircraft components (Wings, Fuselage, Energy systems, etc.)
   - **Methods**: Low-level calculation methods for aerodynamics, weights, etc.
   - **Core**: Fundamental data structures and units system
   - **Plots**: Visualization tools for analysis results

2. **`regression/scripts/`** - Test and validation scripts including:
   - **aerodynamics/**: Aerodynamic analysis tests (Fidelity_Zero, Supersonic)
   - **lifting_line/**: Lifting line theory tests
   - **Vehicles/**: Aircraft configuration definitions (Boeing 737, Concorde, etc.)
   - **propeller/**: Propeller analysis tests
   - Various other analysis modules

3. **`Tutorials-2.3.1/`** and **`Tutorials252/`** - Educational examples and tutorials

## Key Aerodynamics Capabilities

### Analysis Methods Available

1. **Fidelity_Zero**: Low-fidelity aerodynamic analysis using:
   - Vortex Lattice Method (VLM) for inviscid lift calculation
   - Semi-empirical drag buildup methods
   - Compressibility corrections

2. **Supersonic_Zero**: For supersonic flight analysis with:
   - Sears-Haack wave drag calculation
   - Supersonic lift and drag methods

3. **Lifting_Line**: Classical lifting line theory implementation

4. **SU2_Euler**: Higher fidelity CFD interface using SU2 solver

### Vehicle Configurations Available

The repository includes multiple pre-defined aircraft configurations:
- **Boeing_737.py**: Commercial airliner configuration
- **Concorde.py**: Supersonic transport configuration  
- **BWB.py**: Blended Wing Body designs
- **Electric_Multicopter.py**: Multi-rotor configurations
- **Solar_UAV.py**: Solar-powered UAV designs
- Various wing-only configurations for focused analysis

### Aerodynamics Test Scripts

1. **`aerodynamics.py`**: Main aerodynamics regression test
   - Tests Boeing 737 configuration
   - Evaluates lift and drag coefficients across range of conditions
   - Validates against known results

2. **`sears_haack.py`**: Supersonic wave drag validation
   - Tests Sears-Haack body theory implementation
   - Supersonic Mach number conditions (M > 1.0)

3. **`lifting_line.py`**: Lifting line theory validation
   - Tests classical lifting line implementation
   - Compares against theoretical results

## Technical Details

### Dependencies
- **Core**: numpy, scipy, matplotlib
- **Machine Learning**: scikit-learn
- **Visualization**: plotly
- **Units**: Custom pint-based units system

### Analysis Workflow
1. **Vehicle Setup**: Define geometry, mass properties, configurations
2. **Analysis Setup**: Configure aerodynamic analysis method and settings
3. **Conditions Setup**: Define flight conditions (Mach, altitude, angle of attack)
4. **Evaluation**: Run analysis and extract results
5. **Validation**: Compare against reference data or regression results

### Key Features
- **Multi-fidelity approach**: From simple methods to CFD integration
- **Comprehensive vehicle modeling**: Complete aircraft system representation
- **Automated design capabilities**: Optimization and trade studies
- **Extensive validation**: Regression tests against known configurations

## Current Status

The framework has been updated for Python 3.12 compatibility with fixes for:
- Collection imports (MutableMapping, Iterable)
- SciPy function changes (cumtrapz → cumulative_trapezoid, derivative location)
- All required dependencies installed

## Potential Use Cases

1. **Conceptual Aircraft Design**: Early-stage aircraft design and analysis
2. **Educational**: Learning aerospace vehicle design principles  
3. **Research**: Advanced aircraft concepts and technologies
4. **Trade Studies**: Comparing different design options
5. **Optimization**: Automated design optimization workflows

## Next Steps for Aerodynamics Testing

1. Investigate and fix VLM grid setup issues in main aerodynamics test
2. Run simpler lifting line theory tests first
3. Validate supersonic analysis capabilities
4. Create custom test cases for specific scenarios