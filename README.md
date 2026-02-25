# ArduPilot ROS2 Development Workspace

Professional Git submodule-based development workspace for ArduPilot with ROS2 integration, Gazebo simulation, and Micro-ROS support.

## 📋 Overview

This workspace integrates multiple ArduPilot and ROS2 repositories as Git submodules, enabling collaborative development with:
- **12 Git submodules** for external dependencies and ArduPilot packages
- **3 local ROS2 packages** for custom development
- **Clean repository structure** with large files excluded
- **Proper remote configuration** (fork + upstream pattern)

## 🚀 Quick Start

### Clone with All Submodules
```bash
git clone --recurse-submodules https://github.com/Shubham07-bit/ardu_ws.git
cd ardu_ws
```

### Initialize Submodules (if cloned without --recurse-submodules)
```bash
git submodule update --init --recursive
```

### Update All Submodules
```bash
git submodule update --remote --merge
```

## 📦 Submodules (12 Total)

### ArduPilot Core Packages
1. **src/ardupilot** - Main ArduPilot autopilot firmware
   - Fork: https://github.com/Shubham07-bit/ardupilot.git
   - Branch: `master`

2. **src/ardupilot_gazebo** - ArduPilot Gazebo plugin
   - Fork: https://github.com/Shubham07-bit/ardupilot_gazebo.git
   - Branch: `main`

3. **src/ardupilot_gz** - ArduPilot Gazebo integration (ROS2)
   - Fork: https://github.com/Shubham07-bit/ardupilot_gz.git
   - Branch: `main`

4. **src/ardupilot_ros** - ArduPilot ROS2 bridge
   - Fork: https://github.com/Shubham07-bit/ardupilot_ros.git
   - Branch: `humble`

### Simulation & Models
5. **src/ardupilot_sitl_models** - SITL Models for testing
   - Fork: https://github.com/Shubham07-bit/SITL_Models.git
   - Branch: `master`

### ROS2 Middleware & Tools
6. **src/mapviz** - Map visualization for ROS2
   - Fork: https://github.com/Shubham07-bit/mapviz.git
   - Branch: `ros2-devel`

7. **src/marti_common** - Common ROS2 utilities
   - Fork: https://github.com/Shubham07-bit/marti_common.git
   - Branch: `ros2-devel`

8. **src/marti_messages** - Message definitions
   - Fork: https://github.com/Shubham07-bit/marti_messages.git
   - Branch: `ros2-devel`

9. **src/micro_ros_agent** - Micro-ROS Agent for embedded communication
   - Fork: https://github.com/Shubham07-bit/micro-ROS-Agent.git
   - Branch: `kilted`

### Gazebo & DDS
10. **src/ros_gz** - ROS2 and Gazebo integration
    - Fork: https://github.com/Shubham07-bit/ros_gz.git
    - Branch: `ros2`

11. **src/sdformat_urdf** - SDF/URDF format utilities
    - Fork: https://github.com/Shubham07-bit/sdformat_urdf.git
    - Branch: `rolling`

12. **src/Micro-XRCE-DDS-Gen** - Micro-ROS DDS code generator
    - Original: https://github.com/eProsima/Micro-XRCE-DDS-Gen.git
    - Branch: `master`

## 📁 Local ROS2 Packages

These are custom development packages included directly in the workspace:

1. **src/ardupilot_gz_bringup** - Gazebo simulation launch files and configurations
2. **src/autonomus_takeoff_landing** - Autonomous takeoff and landing control
3. **src/iris_drone_controller** - Iris drone control interface

## 🛠️ Build Instructions

### Prerequisites
```bash
sudo apt update
sudo apt install -y \
  ros-humble-desktop \
  gazebo \
  git \
  python3-colcon-common-extensions \
  python3-rosdep
```

### Build Workspace
```bash
cd ardu_ws
source /opt/ros/humble/setup.bash
colcon build
```

### Source Setup
```bash
source install/setup.bash
```

## 🔄 Workflow

### Check Submodule Status
```bash
git submodule status
```

### View Submodule Changes
```bash
git diff --submodule=short
```

### Update from Upstream
```bash
# Update all submodules from their remote origins
git submodule foreach git pull origin $(git config -f .gitmodules submodule.$name.branch || echo main)
```

### Commit Changes with Submodule Updates
```bash
git add .
git commit -m "Update submodules and workspace"
git push origin main
```

## 📖 Documentation

- **MAINTENANCE_GUIDE.md** - Comprehensive workspace maintenance procedures
- **SUBMODULE_CONVERSION_REPORT.md** - Technical details of submodule setup
- Individual package READMEs in each submodule

## ⚙️ Configuration

### .gitignore Exclusions
The workspace excludes:
- Build directories: `build/`, `install/`, `log/`, `logs/`
- Large files: `*.tif`, `terrain/`, `*.tlog`, `*.tlog.raw`
- Debug files: `*.out`, `*.bin`, `*.raw`
- Contribution docs: `/contribution/`
- IDE files: `.vscode/`, `__pycache__/`, `*.pyc`

### Submodule Remote Configuration
Each forked submodule follows this pattern:
- **origin** = Your fork (for pushing)
- **upstream** = Original repository (for syncing)

## 🐛 Troubleshooting

### Submodule is in Detached HEAD
```bash
cd src/submodule_name
git checkout main  # or appropriate branch
cd ../..
git add src/submodule_name
git commit -m "Update submodule to branch"
```

### Submodule Conflicts
```bash
git submodule foreach git status
git submodule update --init --recursive
```

### Large File Issues
Ensure your .gitignore is properly configured before committing large files. Already-committed files over 100MB will block GitHub pushes.

## 🔐 Security Notes

- Always use SSH keys for Git operations: `git config --global url."git@github.com:".insteadOf "https://github.com/"`
- Never commit secrets, API keys, or credentials
- Review `.gitignore` before adding new files

## 📊 Repository Statistics

```bash
# Count all submodules
git submodule status | wc -l

# Show submodule commits
git submodule foreach 'echo "$name: $(git log -1 --oneline)"'

# Check total repository size
du -sh .git/
```

## 🤝 Contributing

1. Create a feature branch in relevant submodule
2. Make changes and test locally
3. Commit with descriptive messages
4. Push to your fork
5. Create pull request to upstream

## 📝 License

Each submodule maintains its own license. Refer to individual repositories for license information.

## 👤 Maintainer

- **GitHub**: [@Shubham07-bit](https://github.com/Shubham07-bit)
- **Workspace**: https://github.com/Shubham07-bit/ardu_ws

## 📞 Support

For issues or questions:
1. Check individual submodule repositories
2. Review MAINTENANCE_GUIDE.md
3. Open issues in the respective repositories

---

**Last Updated**: February 2026
**Repository Version**: 1.0
**Git Submodules**: 12
**Local Packages**: 3
