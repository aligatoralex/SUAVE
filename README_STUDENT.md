# SUAVE Student Environment

Welcome to the SUAVE (Stanford University Aerospace Vehicle Environment) student setup! This repository provides a pre-configured environment for learning aircraft design and analysis.

## 📚 Documentation

- **[Student Setup Guide](STUDENT_SETUP_GUIDE.md)** - Complete setup and usage instructions
- **[Quick Reference Card](STUDENT_QUICK_REFERENCE.md)** - Essential commands and tips
- **[Potential Improvements](STUDENT_IMPROVEMENTS.md)** - Suggestions for making the environment even better

## 🚀 Get Started in 3 Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/suavecode/SUAVE.git
   cd SUAVE
   ```

2. **Start the environment**
   ```bash
   make build    # First time only
   make up       # Start Jupyter
   ```

3. **Open Jupyter Lab**
   - Go to http://localhost:8888
   - Start designing aircraft!

## 🎯 What You Can Do

- **Design aircraft** from concept to analysis
- **Run aerodynamic simulations** using SU2 and AVL
- **Generate 3D meshes** with GMSH
- **Optimize designs** with built-in tools
- **Learn through examples** in the regression folder

## 🛠️ What's Included

- **SUAVE Framework** - Complete aircraft design environment
- **External Tools** - SU2 (CFD), AVL (aerodynamics), GMSH (meshing)
- **Jupyter Lab** - Interactive notebook interface
- **Docker Environment** - No setup conflicts, works everywhere
- **Student Workspace** - Dedicated folders for your projects

## 📁 Project Structure

```
SUAVE/
├── trunk/                    # SUAVE source code
├── student_competition/      # Your work goes here!
├── regression/               # Example scripts
├── docker/                   # Container configuration
├── .devcontainer/            # VS Code integration
└── Makefile                  # Easy commands
```

## 🔧 Available Commands

| Command | What it does |
|---------|--------------|
| `make up` | Start the environment |
| `make down` | Stop the environment |
| `make bash` | Open terminal in container |
| `make logs` | View container logs |
| `make dev-install` | Install SUAVE in development mode |

## 🌟 Why This Setup is Great for Students

- **No Environment Conflicts** - Docker isolates everything
- **Pre-installed Tools** - Everything works out of the box
- **Interactive Learning** - Jupyter notebooks for experimentation
- **Real Examples** - Working code to learn from
- **Professional Tools** - Industry-standard analysis software

## 🆘 Need Help?

1. **Check the logs**: `make logs`
2. **Open terminal**: `make bash`
3. **Read the guides**: Start with the [Setup Guide](STUDENT_SETUP_GUIDE.md)
4. **Official docs**: [suave.stanford.edu](http://suave.stanford.edu)
5. **GitHub issues**: [github.com/suavecode/SUAVE/issues](https://github.com/suavecode/SUAVE/issues)

## 🎓 Learning Path

1. **Start Simple** - Copy examples from `regression/` folder
2. **Modify Parameters** - Change values, see what happens
3. **Build Your Own** - Create aircraft from scratch
4. **Advanced Analysis** - Use optimization and multi-fidelity tools
5. **Share & Collaborate** - Work with classmates on projects

## 🔮 Future Improvements

We're working on making this even better for students! See [Potential Improvements](STUDENT_IMPROVEMENTS.md) for what's coming:

- Interactive setup wizard
- Built-in tutorials
- Better error messages
- Progress tracking
- 3D visualization tools

## 📝 Contributing

Found a bug? Have a suggestion? Want to help other students?

- **Report issues** on GitHub
- **Submit improvements** via pull requests
- **Share examples** with the community
- **Write tutorials** for other students

## 📄 License

This project is licensed under LGPL-2.1. See [LICENSE](LICENSE) for details.

---

**Ready to design the future of aviation?** 🛩️

Start with the [Student Setup Guide](STUDENT_SETUP_GUIDE.md) and let's build something amazing together!