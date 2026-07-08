# SUAVE Student Quick Reference Card

## 🚀 Quick Start Commands

```bash
# First time setup
git clone https://github.com/suavecode/SUAVE.git
cd SUAVE
make build

# Daily use
make up          # Start environment
make down        # Stop environment
make bash        # Open terminal in container
```

## 🌐 Access Points

- **Jupyter Lab**: http://localhost:8888
- **Container Terminal**: `make bash`
- **Logs**: `make logs`

## 📁 Key Directories

```
/workspace/
├── student_competition/    ← YOUR WORK GOES HERE
│   ├── results/           ← Save analysis results
│   └── plots/             ← Save generated plots
├── trunk/                 ← SUAVE source code
└── regression/            ← Example scripts
```

## 🐍 Essential Python Imports

```python
import SUAVE
from SUAVE.Core import Units
from SUAVE.Methods.Geometry.Three_Dimensional import compute_chord_length_from_span_location
```

## 🔧 Available Tools

| Tool | Purpose | Path |
|------|---------|------|
| **SU2** | CFD Analysis | `/opt/su2/bin/SU2_CFD` |
| **AVL** | Aerodynamics | `/usr/local/bin/avl` |
| **GMSH** | Mesh Generation | `/usr/bin/gmsh` |
| **OpenVSP** | Aircraft Modeling | (Coming soon) |

## 📚 Common Patterns

### Basic Aircraft Setup
```python
vehicle = SUAVE.Vehicle()
vehicle.tag = 'my_aircraft'

# Add components
wing = SUAVE.Components.Wings.Main_Wing()
vehicle.add_component(wing)
```

### Units Conversion
```python
from SUAVE.Core import Units

# Convert to SI units
span_ft = 100
span_m = span_ft * Units.ft
```

### Running Analysis
```python
# Mission analysis
mission = SUAVE.Analyses.Mission.Sequential_Segments()
results = mission.evaluate(vehicle)
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't import SUAVE | Run `make dev-install` |
| Port 8888 busy | Run `make down` then `make up` |
| Container won't start | Check Docker is running |
| Analysis fails | Check logs with `make logs` |

## 📖 Learning Path

1. **Start Here**: `student_competition/` folder
2. **First Example**: Copy from `regression/` folder
3. **Modify**: Change parameters, see what happens
4. **Create**: Build your own aircraft design
5. **Optimize**: Use SUAVE's optimization tools

## 🎯 Pro Tips

- **Always work in `student_competition/`** - keeps your work safe
- **Use Jupyter notebooks** - great for learning and documentation
- **Save frequently** - results and plots in dedicated folders
- **Start simple** - begin with basic aircraft, add complexity gradually
- **Check examples** - `regression/` folder has working code to learn from

## 📞 Getting Help

- **Container logs**: `make logs`
- **Open terminal**: `make bash`
- **Official docs**: [suave.stanford.edu](http://suave.stanford.edu)
- **GitHub**: [github.com/suavecode/SUAVE](https://github.com/suavecode/SUAVE)

---

**Remember**: This is a learning environment! Experiment, make mistakes, and learn from them. The SUAVE community is here to help you succeed in aircraft design.