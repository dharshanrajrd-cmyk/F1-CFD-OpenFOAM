# F1 CFD OpenFOAM

**Parametric F1 race car CFD simulation with OpenFOAM**

Generate realistic F1-style race car geometries, mesh them with snappyHexMesh, and run transient aerodynamic simulations using OpenFOAM.

---

## Quick Start

### 1. Generate F1 Car Geometry

```bash
# Install dependencies
pip install cadquery

# Generate full-size F1 car
python3 generate_f1_car.py --output f1_car.stl

# Or at half scale for faster meshing
python3 generate_f1_car.py --scale 0.5 --output f1_car_half.stl

# With DRS (Drag Reduction System) open
python3 generate_f1_car.py --drs-open --output f1_car_drs.stl
```

### 2. Create OpenFOAM Case

```bash
# Create case directory structure
mkdir -p f1_cfd/{constant/triSurface,system,0}
cd f1_cfd

# Copy generated geometry
cp ../f1_car.stl constant/triSurface/
```

### 3. Mesh with snappyHexMesh

```bash
# Copy mesh configuration
cp ../casefiles/* system/

# Generate base mesh
blockMesh

# Extract surface features
surfaceFeatureExtract -includedAngle 150 -writeObj \
  constant/triSurface/f1_car.stl

# Refine around car geometry
snappyHexMesh -overwrite

# Check mesh quality
checkMesh
```

### 4. Run CFD Simulation

```bash
# Copy initial conditions
cp -r ../0 .

# Run steady-state simulation
simpleFoam > log.simpleFoam &

# Monitor convergence
tail -f log.simpleFoam

# Post-process results
paraFoam
```

---

## Features

### Parametric Geometry
- **Full-size F1 dimensions**: 5.6m length × 2.6m width × 1.2m height
- **Configurable scale**: Run at any scale (0.1x to 1.0x)
- **Detailed components**:
  - Main chassis/monocoque with nose cone
  - Cockpit and roll hoop
  - Multi-element front wing (3 flaps)
  - Rear wing with DRS (Drag Reduction System)
  - Rear diffuser for ground effect
  - Realistic wheel geometry
  - Engine sidepods
  - Side mirrors
  - Undercarriage

### OpenFOAM Ready
- Exports directly to **STL format** (triangulated surface)
- Optimized for `snappyHexMesh` automatic refinement
- Includes complete case setup files
- Boundary conditions pre-configured for aerodynamic simulation
- Force coefficient extraction (Cd, Cl, etc.)

### Aerodynamic Features
- **Front wing**: 3-element profile for downforce optimization
- **Rear wing**: DRS-capable for speed configurations
- **Diffuser**: Ground effect modeling
- **Ride height**: Configurable suspension geometry
- **Wheel positioning**: Realistic F1 chassis geometry

---

## File Structure

```
F1-CFD-OpenFOAM/
├── generate_f1_car.py              # Main CadQuery geometry generator
├── casefiles/                       # OpenFOAM configuration templates
│   ├── blockMeshDict                # Base hexahedral mesh definition
│   ├── snappyHexMeshDict            # Automatic refinement around car
│   ├── controlDict                  # Solver and runtime control
│   ├── fvSchemes                    # Discretization schemes
│   ├── fvSolution                   # Solver settings (SIMPLE algorithm)
│   ├── forceCoeffs                  # Force extraction function
│   └── momentumTransport            # k-ω SST turbulence model
├── 0/                               # Initial/boundary conditions
│   ├── U                            # Velocity field
│   ├── p                            # Pressure field
│   ├── nut                          # Turbulent viscosity
│   ├── k                            # Turbulent kinetic energy
│   └── omega                        # Specific dissipation rate
├── examples/                        # Worked examples and tutorials
├── docs/                            # Detailed documentation
└── README.md                        # This file
```

---

## Usage Examples

### Example 1: Standard F1 Car Simulation

```bash
# Generate at full scale
python3 generate_f1_car.py --output f1_car.stl

# Create OpenFOAM case
mkdir -p f1_case/{constant/triSurface,system,0}
cd f1_case
cp ../f1_car.stl constant/triSurface/
cp ../casefiles/* system/
cp -r ../0 .

# Mesh and simulate
blockMesh
surfaceFeatureExtract -includedAngle 150 -writeObj constant/triSurface/f1_car.stl
snappyHexMesh -overwrite
checkMesh
simpleFoam > log.simpleFoam &
```

### Example 2: DRS-Open Configuration

```bash
# Generate with DRS flap open (reduced downforce, higher speed)
python3 generate_f1_car.py --drs-open --output f1_car_drs_open.stl

# Mesh and compare forces vs DRS-closed
# (Cd and Cl will show reduced downforce)
```

### Example 3: Scale Studies

```bash
# Generate at multiple scales for computational speed vs accuracy tradeoff
python3 generate_f1_car.py --scale 1.0 --output f1_car_full.stl    # ~5MB STL
python3 generate_f1_car.py --scale 0.5 --output f1_car_half.stl    # ~0.6MB STL
python3 generate_f1_car.py --scale 0.25 --output f1_car_quarter.stl # ~0.08MB STL

# Half-scale example: faster meshing, suitable for parameter studies
# Quarter-scale: rapid prototyping and validation
```

---

## OpenFOAM Simulation Details

### Domain Setup

```
┌─────────────────────────────────────────────────────────────┐
│  Inlet          Car          Wake Region        Outlet      │
│  ◄─────► ┌──────────┐  ◄─────────────────►  ◄───────────►  │
│   ~5L    │   F1     │        ~10-15L              ~5L       │
│          │   Car    │                                        │
│          └──────────┘                                        │
└─────────────────────────────────────────────────────────────┘

  L = car length (~5.6 m)
  Domain: 5L upstream × 20L downstream × 3L height
  Symmetry plane: model half for computational efficiency
```

### Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Inlet velocity** | 50-100 m/s | Typical F1 race speeds |
| **Turbulence model** | k-ω SST | Best for external aerodynamics |
| **Solver** | simpleFoam | Steady-state incompressible |
| **Mesh y+** | < 1.0 | Wall-resolved boundary layer |
| **Domain cells** | 2-5M | Depending on scale |
| **Reference velocity** | 89 m/s (320 km/h) | F1 characteristic speed |
| **Reynolds number** | ~5×10⁶ | Highly turbulent regime |

### Force Coefficients

The simulation automatically extracts:

```
Cd  = Drag Coefficient = Drag / (0.5 × ρ × U² × Aref)
Cl  = Lift Coefficient = Lift / (0.5 × ρ × U² × Aref)
Cl/Cd = Aerodynamic Efficiency

where:
  ρ = air density (1.225 kg/m³)
  U = freestream velocity (m/s)
  Aref = reference area (frontal area, ~1.5 m²)
```

**Typical F1 Values:**
- **Cd**: 0.7-1.0 (depends on wing configuration)
- **Cl**: 2.0-3.5 (high downforce for cornering grip)
- **Balance**: Front/rear downforce ratio ~65%/35%

---

## Customization

### Modify Car Dimensions

Edit `generate_f1_car.py` class parameters:

```python
class F1RaceCar:
    def __init__(self, scale=1.0):
        self.overall_length = 5600 * scale        # mm
        self.overall_width = 2600 * scale         # mm
        self.cockpit_x = 1500 * scale             # mm
        self.front_wing_chord = 300 * scale       # Depth
        self.rear_wing_height = 600 * scale       # Height
        # ... etc
```

### Adjust Wing Angles

Modify wing flap angles in `create_front_wing()` and `create_rear_wing()`:

```python
.rotate((0,0,0), (1,0,0), 25)  # 25° flap angle
```

### Change Mesh Resolution

Edit `snappyHexMeshDict`:

```c++
refinementSurfaces
{
    car
    {
        level (4 6);  // (min max) refinement levels
    }
}

addLayersControls
{
    nSurfaceLayers 5;        // Boundary layer cells
    expansionRatio 1.2;      // Growth between layers
}
```

---

## Requirements

### Software
- **OpenFOAM v2212+** (ESI or Foundation version)
- **Python 3.7+**
- **ParaView** (for visualization)
- **Salome** or **Gmsh** (optional, for mesh inspection)

### Python Dependencies
```bash
pip install cadquery numpy matplotlib
```

### System Resources

| Scale | Domain Cells | RAM | CPU Time | Disk |
|-------|--------------|-----|----------|------|
| 0.25x | ~200K | 1 GB | ~2-4 hrs | 100 MB |
| 0.5x | ~1M | 4 GB | ~8-12 hrs | 500 MB |
| 1.0x | ~5M | 16 GB | ~24-48 hrs | 2 GB |

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  1. Generate Geometry (CadQuery)                            │
│     python3 generate_f1_car.py --output f1_car.stl          │
└────────────────────┬────────────────────────────────────────┘
                     │ f1_car.stl
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Create OpenFOAM Case                                    │
│     ├── constant/triSurface/f1_car.stl                      │
│     ├── system/blockMeshDict, snappyHexMeshDict, etc.       │
│     └── 0/U, p, k, omega                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Mesh Generation                                         │
│     blockMesh → surfaceFeatureExtract → snappyHexMesh       │
└────────────────────┬────────────────────────────────────────┘
                     │ Mesh (polymesh)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. CFD Simulation                                          │
│     simpleFoam (k-ω SST, SIMPLE algorithm)                  │
└────────────────────┬────────────────────────────────────────┘
                     │ Solution fields (U, p, k, ω)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Post-Processing & Visualization                         │
│     ├── paraFoam (3D flow visualization)                    │
│     ├── forceCoeffs (Cd, Cl extraction)                     │
│     └── Python analysis (force balances, etc.)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### CadQuery Export Fails

**Problem**: `ModuleNotFoundError: No module named 'cadquery'`

**Solution**:
```bash
pip install --upgrade cadquery
```

### STL Quality Issues

**Problem**: `snappyHexMesh` fails or produces poor quality mesh

**Solution**:
1. Verify STL integrity:
   ```bash
   surfaceCheck constant/triSurface/f1_car.stl
   ```
2. Repair if needed (gaps, holes, non-manifold edges)
3. Reduce scale and retry

### High Memory Usage

**Problem**: Mesh generation runs out of RAM

**Solution**:
- Reduce scale factor: `--scale 0.5`
- Decrease mesh refinement levels in `snappyHexMeshDict`
- Split domain into multiple regions
- Run on HPC cluster

### Slow Convergence

**Problem**: `simpleFoam` doesn't converge in reasonable time

**Solution**:
1. Increase relaxation factors in `fvSolution`:
   ```c++
   relaxationFactors { U 0.8; p 0.4; }
   ```
2. Use coarser mesh for initial simulation
3. Switch to `pimpleFoam` for transient effects
4. Reduce inlet velocity for initial runs

---

## References

### CFD & Aerodynamics
- OpenFOAM User Guide: https://cfd.direct/openfoam/user-guide/
- Aerodynamics of Road and Race Vehicles (Hucho et al.)
- F1 Technical Regulations 2024: https://www.fia.com/

### CadQuery Documentation
- CadQuery Docs: https://cadquery.readthedocs.io/
- CadQuery GitHub: https://github.com/CadQuery/cadquery

### Tools & Resources
- OpenFOAM: https://openfoam.org/
- ParaView: https://www.paraview.org/
- Salome Platform: https://www.salome-platform.org/

---

## Contributing

Contributions welcome! Areas for enhancement:
- [ ] Add parametric suspension geometry
- [ ] Implement movable ground boundary condition
- [ ] Add DRS actuation mechanism animation
- [ ] Create wind tunnel domain variants
- [ ] Multi-configuration comparison studies
- [ ] Machine learning design optimization

---

## License

MIT License - Free for academic and commercial use.

---

## Authors

Generated for F1 CFD OpenFOAM project.

For questions or issues, please open an issue on GitHub.

---

**Last Updated**: September 2026

**Status**: Production Ready ✓
