#!/usr/bin/env python3
"""
Parametric F1 Race Car Geometry Generator using CadQuery

Generates a realistic F1-style car with:
  - Main chassis/monocoque
  - Front wing with multiple elements
  - Rear wing (DRS-capable)
  - Engine and sidepods
  - Wheels and suspension
  - Diffuser
  - Cockpit cowl

Exports to STL for OpenFOAM CFD simulations.

Usage:
  python3 generate_f1_car.py [--output racecar.stl] [--scale 1.0]
  python3 generate_f1_car.py --preview  # Open in 3D viewer

Dependencies:
  pip install cadquery

Author: Generated for F1 CFD OpenFOAM
"""

import cadquery as cq
from cadquery import Workplane, Plane, Vector
import math
import argparse
import sys
from pathlib import Path


class F1RaceCar:
    """
    Parametric F1 race car geometry builder.
    All dimensions in millimeters (mm).
    """

    def __init__(self, scale=1.0, verbose=True):
        """
        Initialize F1 car with configurable parameters.
        
        Args:
            scale (float): Scale factor for all dimensions (default: 1.0 = full size)
            verbose (bool): Print generation steps
        """
        self.scale = scale
        self.verbose = verbose
        self._log = self._print if verbose else lambda x: None
        
        # ─── MAIN DIMENSIONS ─────────────────────────────────────────────────
        # Based on F1 technical regulations (2024)
        self.overall_length = 5600 * scale        # mm
        self.overall_width = 2600 * scale         # mm (with mirrors)
        self.chassis_width = 1700 * scale         # mm (without mirrors)
        self.overall_height = 1200 * scale        # mm
        
        self.wheelbase = 3700 * scale             # mm (distance between axles)
        self.track_width = 1470 * scale           # mm (wheel to wheel)
        
        # Cockpit
        self.cockpit_x = 1500 * scale
        self.cockpit_y = 1400 * scale
        self.cockpit_z = 400 * scale
        self.cockpit_start = 2000 * scale
        
        # Wings
        self.front_wing_chord = 300 * scale       # Depth of front wing
        self.rear_wing_chord = 250 * scale        # Depth of rear wing
        self.front_wing_x = 500 * scale           # Distance from nose
        self.rear_wing_x = self.overall_length - 700 * scale
        
        # Wheels
        self.wheel_diameter = 370 * scale         # mm
        self.wheel_radius = self.wheel_diameter / 2
        self.front_axle_x = 1800 * scale
        self.rear_axle_x = self.front_axle_x + self.wheelbase
        self.left_wheel_y = -self.track_width / 2
        self.right_wheel_y = self.track_width / 2
        
        # Aerodynamic elements
        self.ride_height = 400 * scale            # Ground clearance
        self.front_wing_height = 250 * scale
        self.rear_wing_height = 600 * scale
        
    def _print(self, msg):
        """Print log message with timestamp."""
        print(f"  ✓ {msg}")
    
    # ────────────────────────────────────────────────────────────────────────
    # CHASSIS & MONOCOQUE
    # ────────────────────────────────────────────────────────────────────────
    
    def create_chassis(self):
        """
        Create main chassis/monocoque structure.
        Includes nose cone, side pods, and basic body shape.
        """
        self._log("Creating chassis/monocoque...")
        
        # Main body box (simplified monocoque)
        body_length = 3500 * self.scale
        body_width = self.chassis_width
        body_height = 600 * self.scale
        
        chassis = (
            Workplane("XY")
            .box(body_length, body_width, body_height)
            .translate((body_length/2 + 800*self.scale, 0, self.ride_height + body_height/2))
        )
        
        # Nose cone (front body)
        nose_length = 800 * self.scale
        nose = (
            Workplane("XY")
            .workplane(offset=self.ride_height + body_height)
            .moveTo(0, 0)
            .spline([(0, 0), (nose_length*0.5, self.chassis_width*0.3), (nose_length, 0)])
            .close()
            .extrude(-body_height * 0.7)
        )
        
        return chassis.union(nose)
    
    def create_cockpit(self):
        """
        Create driver cockpit (raised area with roll hoop).
        """
        self._log("Creating cockpit and roll hoop...")
        
        # Cockpit canopy (raised area)
        cockpit = (
            Workplane("XY")
            .box(self.cockpit_x, self.cockpit_y, self.cockpit_z)
            .translate((
                self.cockpit_start + self.cockpit_x/2,
                0,
                self.ride_height + 600*self.scale + self.cockpit_z/2
            ))
        )
        
        # Roll hoop (vertical protection structure)
        hoop_diameter = 150 * self.scale
        hoop_height = 600 * self.scale
        
        roll_hoop = (
            Workplane("XY")
            .cylinder(hoop_height, hoop_diameter/2)
            .translate((
                self.cockpit_start + self.cockpit_x*0.7,
                0,
                self.ride_height + 900*self.scale
            ))
        )
        
        return cockpit.union(roll_hoop)
    
    # ────────────────────────────────────────────────────────────────────────
    # FRONT WING
    # ────────────────────────────────────────────────────────────────────────
    
    def create_front_wing(self):
        """
        Create front wing with multiple elements for downforce.
        Simplified model of modern F1 front wing.
        """
        self._log("Creating front wing with flap elements...")
        
        wing_y = self.chassis_width / 2 + 100 * self.scale  # Extends beyond body
        wing_elements = []
        
        # Main front wing plane
        main_wing = (
            Workplane("XY")
            .box(
                self.front_wing_chord,
                self.chassis_width + 400*self.scale,
                50*self.scale
            )
            .translate((
                self.front_wing_x + self.front_wing_chord/2,
                0,
                self.ride_height + self.front_wing_height
            ))
        )
        wing_elements.append(main_wing)
        
        # Flap 1 (middle)
        flap1 = (
            Workplane("XY")
            .box(
                self.front_wing_chord * 0.8,
                self.chassis_width + 350*self.scale,
                40*self.scale
            )
            .rotate((0,0,0), (1,0,0), 25)  # 25° angle
            .translate((
                self.front_wing_x + self.front_wing_chord * 1.3,
                0,
                self.ride_height + self.front_wing_height - 150*self.scale
            ))
        )
        wing_elements.append(flap1)
        
        # Flap 2 (outer)
        flap2 = (
            Workplane("XY")
            .box(
                self.front_wing_chord * 0.6,
                self.chassis_width + 300*self.scale,
                40*self.scale
            )
            .rotate((0,0,0), (1,0,0), 45)  # 45° angle
            .translate((
                self.front_wing_x + self.front_wing_chord * 1.7,
                0,
                self.ride_height + self.front_wing_height - 250*self.scale
            ))
        )
        wing_elements.append(flap2)
        
        # Combine all wing elements
        front_wing = wing_elements[0]
        for wing in wing_elements[1:]:
            front_wing = front_wing.union(wing)
        
        return front_wing
    
    # ────────────────────────────────────────────────────────────────────────
    # REAR WING
    # ────────────────────────────────────────────────────────────────────────
    
    def create_rear_wing(self, drs_open=False):
        """
        Create rear wing with DRS (Drag Reduction System) flap.
        
        Args:
            drs_open (bool): If True, rear wing flap is open (reduced downforce)
        """
        self._log(f"Creating rear wing (DRS {'OPEN' if drs_open else 'CLOSED'})...")
        
        wing_y = self.chassis_width / 2 + 150 * self.scale
        
        # Main rear wing endplate (vertical)
        main_wing = (
            Workplane("XY")
            .box(
                self.rear_wing_chord,
                self.chassis_width + 500*self.scale,
                100*self.scale
            )
            .translate((
                self.rear_wing_x + self.rear_wing_chord/2,
                0,
                self.ride_height + self.rear_wing_height
            ))
        )
        
        if drs_open:
            # DRS flap opened (angled back)
            drs_flap = (
                Workplane("XY")
                .box(
                    self.rear_wing_chord * 0.5,
                    self.chassis_width + 450*self.scale,
                    80*self.scale
                )
                .rotate((0,0,0), (1,0,0), -35)  # Angled back
                .translate((
                    self.rear_wing_x + self.rear_wing_chord * 0.8,
                    0,
                    self.ride_height + self.rear_wing_height + 200*self.scale
                ))
            )
        else:
            # DRS flap closed (upright)
            drs_flap = (
                Workplane("XY")
                .box(
                    self.rear_wing_chord * 0.5,
                    self.chassis_width + 450*self.scale,
                    100*self.scale
                )
                .translate((
                    self.rear_wing_x + self.rear_wing_chord * 0.8,
                    0,
                    self.ride_height + self.rear_wing_height + 250*self.scale
                ))
            )
        
        return main_wing.union(drs_flap)
    
    # ────────────────────────────────────────────────────────────────────────
    # DIFFUSER & UNDERBODY
    # ────────────────────────────────────────────────────────────────────────
    
    def create_diffuser(self):
        """
        Create rear diffuser for ground effect (aerodynamic downforce).
        Accelerates airflow under the car.
        """
        self._log("Creating rear diffuser...")
        
        # Diffuser starts after main body
        diffuser_length = 600 * self.scale
        diffuser_height_inlet = 200 * self.scale
        diffuser_height_outlet = 500 * self.scale
        
        diffuser = (
            Workplane("XY")
            .workplane(offset=self.ride_height + diffuser_height_inlet/2)
            .moveTo(0, -self.chassis_width/2)
            .lineTo(0, self.chassis_width/2)
            .lineTo(diffuser_length, self.chassis_width/2 + 200*self.scale)
            .lineTo(diffuser_length, -self.chassis_width/2 - 200*self.scale)
            .close()
            .extrude(diffuser_height_outlet - diffuser_height_inlet)
            .translate((self.rear_axle_x + 400*self.scale, 0, 0))
        )
        
        return diffuser
    
    # ────────────────────────────────────────────────────────────────────────
    # WHEELS
    # ────────────────────────────────────────────────────────────────────────
    
    def create_wheels(self):
        """
        Create four wheels (tires).
        """
        self._log("Creating wheels (4x)...")
        
        wheels = []
        
        # Front left wheel
        fl_wheel = (
            Workplane("XY")
            .sphere(self.wheel_radius)
            .translate((self.front_axle_x, self.left_wheel_y, self.wheel_radius))
        )
        wheels.append(fl_wheel)
        
        # Front right wheel
        fr_wheel = (
            Workplane("XY")
            .sphere(self.wheel_radius)
            .translate((self.front_axle_x, self.right_wheel_y, self.wheel_radius))
        )
        wheels.append(fr_wheel)
        
        # Rear left wheel
        rl_wheel = (
            Workplane("XY")
            .sphere(self.wheel_radius)
            .translate((self.rear_axle_x, self.left_wheel_y, self.wheel_radius))
        )
        wheels.append(rl_wheel)
        
        # Rear right wheel
        rr_wheel = (
            Workplane("XY")
            .sphere(self.wheel_radius)
            .translate((self.rear_axle_x, self.right_wheel_y, self.wheel_radius))
        )
        wheels.append(rr_wheel)
        
        return wheels
    
    # ────────────────────────────────────────────────────────────────────────
    # ENGINE & SIDEPODS
    # ────────────────────────────────────────────────────────────────────────
    
    def create_sidepods(self):
        """
        Create engine/power unit sidepods (air intake areas).
        """
        self._log("Creating sidepods...")
        
        sidepod_length = 1200 * self.scale
        sidepod_height = 350 * self.scale
        sidepod_width = 200 * self.scale
        
        # Left sidepod
        left_sidepod = (
            Workplane("XY")
            .box(sidepod_length, sidepod_width, sidepod_height)
            .translate((
                self.cockpit_start + sidepod_length/2,
                -self.chassis_width/2 - sidepod_width/2,
                self.ride_height + 300*self.scale
            ))
        )
        
        # Right sidepod
        right_sidepod = (
            Workplane("XY")
            .box(sidepod_length, sidepod_width, sidepod_height)
            .translate((
                self.cockpit_start + sidepod_length/2,
                self.chassis_width/2 + sidepod_width/2,
                self.ride_height + 300*self.scale
            ))
        )
        
        return left_sidepod.union(right_sidepod)
    
    # ────────────────────────────────────────────────────────────────────────
    # SUSPENSION & MISC
    # ────────────────────────────────────────────────────────────────────────
    
    def create_mirrors(self):
        """
        Create side mirrors for realistic appearance.
        """
        self._log("Creating side mirrors...")
        
        mirror_width = 150 * self.scale
        mirror_height = 200 * self.scale
        mirror_depth = 80 * self.scale
        
        # Left mirror
        left_mirror = (
            Workplane("XY")
            .box(mirror_depth, mirror_width, mirror_height)
            .translate((
                self.cockpit_start,
                -self.chassis_width/2 - 250*self.scale,
                self.ride_height + 500*self.scale
            ))
        )
        
        # Right mirror
        right_mirror = (
            Workplane("XY")
            .box(mirror_depth, mirror_width, mirror_height)
            .translate((
                self.cockpit_start,
                self.chassis_width/2 + 250*self.scale,
                self.ride_height + 500*self.scale
            ))
        )
        
        return left_mirror.union(right_mirror)
    
    # ────────────────────────────────────────────────────────────────────────
    # ASSEMBLY
    # ────────────────────────────────────────────────────────────────────────
    
    def build_complete_car(self, drs_open=False):
        """
        Assemble complete F1 car from all components.
        
        Args:
            drs_open (bool): Open rear wing DRS flap
            
        Returns:
            Compound object containing entire car
        """
        self._log("Assembling complete F1 race car...")
        
        # Create all components
        chassis = self.create_chassis()
        cockpit = self.create_cockpit()
        front_wing = self.create_front_wing()
        rear_wing = self.create_rear_wing(drs_open=drs_open)
        diffuser = self.create_diffuser()
        wheels = self.create_wheels()
        sidepods = self.create_sidepods()
        mirrors = self.create_mirrors()
        
        # Union all main components
        car = (
            chassis
            .union(cockpit)
            .union(front_wing)
            .union(rear_wing)
            .union(diffuser)
            .union(sidepods)
            .union(mirrors)
        )
        
        # Union all wheels
        for wheel in wheels:
            car = car.union(wheel)
        
        self._log("Assembly complete!")
        return car
    
    def export_stl(self, filename, drs_open=False):
        """
        Build car and export to STL file for OpenFOAM.
        
        Args:
            filename (str): Output STL filename
            drs_open (bool): Open rear wing DRS flap
        """
        self._log(f"Building F1 car (scale={self.scale})...")
        car = self.build_complete_car(drs_open=drs_open)
        
        self._log(f"Exporting to {filename}...")
        cq.exporters.export(car, filename)
        
        file_size_mb = Path(filename).stat().st_size / (1024**2)
        self._log(f"Export complete: {file_size_mb:.2f} MB")
        
        return car


def main():
    """
    Command-line interface for F1 car generation.
    """
    parser = argparse.ArgumentParser(
        description="Generate parametric F1 race car geometry with CadQuery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_f1_car.py --output racecar.stl
  python3 generate_f1_car.py --scale 0.5 --output half_scale.stl
  python3 generate_f1_car.py --drs-open --output drs_open.stl
  python3 generate_f1_car.py --preview
        """
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="f1_racecar.stl",
        help="Output STL filename (default: f1_racecar.stl)"
    )
    
    parser.add_argument(
        "-s", "--scale",
        type=float,
        default=1.0,
        help="Scale factor for all dimensions (default: 1.0 = full size)"
    )
    
    parser.add_argument(
        "--drs-open",
        action="store_true",
        help="Open rear wing DRS flap (reduced downforce configuration)"
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Open 3D preview in CAD viewer (requires GUI)"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    # Create car generator
    print("\n" + "="*60)
    print("  F1 RACE CAR GEOMETRY GENERATOR WITH CADQUERY")
    print("="*60 + "\n")
    
    generator = F1RaceCar(scale=args.scale, verbose=not args.quiet)
    
    # Export to STL
    car = generator.export_stl(args.output, drs_open=args.drs_open)
    
    # Show preview if requested
    if args.preview:
        print("\n  Opening 3D preview...")
        try:
            from cadquery import View
            View(car)
        except ImportError:
            print("  Warning: 3D preview requires additional dependencies")
            print("  Install with: pip install cadquery[gui]")
    
    print("\n" + "="*60)
    print(f"  ✓ F1 car successfully generated: {args.output}")
    print(f"  Scale: {args.scale}x")
    print(f"  DRS: {'OPEN' if args.drs_open else 'CLOSED'}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
