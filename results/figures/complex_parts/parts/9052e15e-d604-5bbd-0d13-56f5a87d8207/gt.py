from build123d import *

horizontal_arm_length = 80.0
vertical_arm_length = 60.0
arm_width = 20.0
arm_thickness = 8.0
rib_height = 6.0
rib_thickness = 4.0
hole_spacing = 30.0
hole_diameter = 5.0
cbore_diameter = 8.0
cbore_depth = 3.0
fillet_radius = 2.0

import math

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_arm_length, 0), (horizontal_arm_length, arm_thickness),
                     (rib_thickness, arm_thickness), (rib_thickness, vertical_arm_length + arm_thickness),
                     (0, vertical_arm_length + arm_thickness), (0, 0), close=True)
        make_face()
    extrude(amount=arm_width)

solid_body = p.part

# Add reinforcing rib on outer vertical face (>Y face)
rib = Pos(rib_thickness/2, vertical_arm_length + arm_thickness + arm_width/2, arm_width/2) * Box(rib_thickness, arm_width, rib_height)
solid_body = solid_body + rib

# Counterbored holes on horizontal arm (top face)
for dx in [-hole_spacing/2, hole_spacing/2]:
    px = horizontal_arm_length/2 + dx
    py = arm_thickness/2
    shaft = Pos(px, py, 0) * Cylinder(hole_diameter/2, arm_width + 10)
    cbore = Pos(px, py, 0) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - shaft - cbore

# Fillet at inner corner where arms meet
all_z_edges = solid_body.edges().filter_by(Axis.Z)
target = Vector(rib_thickness, arm_thickness, arm_width/2)
inner_edge = min(all_z_edges, key=lambda e: (e.center() - target).Length)
solid_body = fillet([inner_edge], fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, OUTPUT_PATH)