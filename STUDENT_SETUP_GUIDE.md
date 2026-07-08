# SUAVE Student Environment Setup Guide

## Overview

This guide explains how to set up and use the SUAVE (Stanford University Aerospace Vehicle Environment) development environment designed specifically for students. The environment provides a pre-configured Docker container with all necessary tools for aircraft design and analysis.

## What is SUAVE?

SUAVE is a multi-fidelity conceptual design environment for designing future aircraft incorporating advanced technologies. It's an open-source Python framework that enables:

- Aircraft conceptual design and analysis
- Multi-fidelity optimization
- Integration with external tools (SU2, AVL, OpenVSP, GMSH)
- Jupyter notebook-based workflows

## Quick Start (Recommended for Students)

### Prerequisites
- Docker Desktop installed on your system
- Git (to clone the repository)
- At least 4GB of available RAM

### 1. Clone the Repository
```bash
git clone https://github.com/suavecode/SUAVE.git
cd SUAVE
```

### 2. Start the Environment
```bash
# Build the Docker image (first time only)
make build

# Start the Jupyter environment
make up
```

### 3. Access Jupyter Lab
- Open your web browser and go to: `http://localhost:8888`
- The environment is ready to use!

### 4. Stop the Environment
```bash
make down
```

## Available Commands

The project includes a convenient Makefile with these commands:

| Command | Description |
|---------|-------------|
| `make build` | Build the Docker image locally |
| `make up` | Start the Jupyter container |
| `make down` | Stop and remove the container |
| `make bash` | Open a bash shell in the running container |
| `make logs` | View container logs |
| `make dev-install` | Install SUAVE in development mode |

## What's Included in the Environment

### Core Tools
- **Python 3.10** with scientific computing packages
- **SUAVE Framework** - The main aircraft design environment
- **Jupyter Lab** - Interactive notebook interface
- **Git LFS** - For handling large files

### External Analysis Tools
- **SU2** (v8.2.0) - Computational Fluid Dynamics solver
- **AVL** (v3.40b) - Aircraft vortex lattice analysis
- **GMSH** - 3D finite element mesh generator
- **OpenVSP** - Vehicle Sketch Pad (placeholder for future integration)

### Python Packages
- numpy, scipy, matplotlib
- scikit-learn
- plotly (for interactive plots)
- jupyter and related tools

## Environment Variables

The container automatically sets these environment variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHONPATH` | `/workspace/trunk:/workspace/student_competition` | Python module search path |
| `SU2_HOME` | `/opt/su2` | SU2 installation directory |
| `SU2_BIN` | `/opt/su2/bin/SU2_CFD` | SU2 executable path |
| `AVL_BIN` | `/usr/local/bin/avl` | AVL executable path |
| `GMSH_BIN` | `/usr/bin/gmsh` | GMSH executable path |

## Directory Structure

```
/workspace/
├── trunk/                    # SUAVE source code
├── student_competition/      # Student work directory
│   ├── results/             # Analysis results
│   └── plots/               # Generated plots
├── regression/               # Test scripts
└── templates/                # Example templates
```

## Working with SUAVE

### 1. Create a New Analysis
Navigate to the `student_competition` folder and create a new Python file or Jupyter notebook.

### 2. Import SUAVE
```python
import SUAVE
from SUAVE.Core import Units
from SUAVE.Methods.Geometry.Three_Dimensional import compute_chord_length_from_span_location
```

### 3. Basic Aircraft Analysis Example
```python
import SUAVE
from SUAVE.Core import Units
from SUAVE.Methods.Geometry.Three_Dimensional import compute_chord_length_from_span_location

# Create a vehicle
vehicle = SUAVE.Vehicle()
vehicle.tag = 'example_aircraft'

# Add wings, engines, etc.
# ... (see SUAVE tutorials for detailed examples)

# Run analysis
# ... (analysis code)
```

## Troubleshooting

### Common Issues

1. **Port 8888 already in use**
   ```bash
   # Stop any existing containers
   make down
   
   # Or change the port in docker-compose.yml
   ```

2. **Docker build fails**
   ```bash
   # Clean up and rebuild
   docker system prune -f
   make build
   ```

3. **Jupyter not accessible**
   - Check if container is running: `docker ps`
   - View logs: `make logs`
   - Ensure no firewall is blocking port 8888

### Getting Help
- Check the container logs: `make logs`
- Open a bash shell: `make bash`
- Visit the SUAVE documentation: [suave.stanford.edu](http://suave.stanford.edu)

## Advanced Usage

### Customizing the Environment
You can modify `docker-compose.yml` to:
- Change Python version
- Add more external tools
- Modify environment variables
- Change port mappings

### Adding New Tools
To add new analysis tools:
1. Modify the `Dockerfile` to download and install the tool
2. Update environment variables in `docker-compose.yml`
3. Rebuild the image: `make build`

### Development Mode
For students working on SUAVE itself:
```bash
make dev-install
```
This installs SUAVE in editable mode, allowing you to modify the source code.

## Best Practices for Students

1. **Always work in the `student_competition` folder** - This keeps your work separate from the SUAVE source code
2. **Use Jupyter notebooks** - They're great for learning and documenting your analysis
3. **Save results and plots** - Use the provided `results/` and `plots/` directories
4. **Version control your work** - Consider using Git for your student projects
5. **Start with examples** - Check the `regression/` folder for working examples

## Next Steps

1. **Complete SUAVE Tutorials**: Visit [suave.stanford.edu](http://suave.stanford.edu) for comprehensive tutorials
2. **Join the Community**: Participate in SUAVE forums and discussions
3. **Explore Examples**: Study the regression test scripts for real-world usage patterns
4. **Build Your Own Aircraft**: Start with simple designs and gradually increase complexity

## Support and Resources

- **Official Documentation**: [suave.stanford.edu](http://suave.stanford.edu)
- **GitHub Repository**: [github.com/suavecode/SUAVE](https://github.com/suavecode/SUAVE)
- **Community Forum**: Available through the official website
- **Academic Support**: Contact your course instructor or TA

---

*This guide is designed to get you started quickly with SUAVE. For advanced usage and detailed API documentation, please refer to the official SUAVE documentation.*