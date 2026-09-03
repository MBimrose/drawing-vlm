from build123d import *
import math

gear_root_radius = 30.0
gear_thickness = 15.0
tooth_height = 6.0
tooth_width = 8.0
num_teeth = 20
central_hole_diameter = 6.0
keyway_width = 4.0
keyway_depth = 3.0
chamfer_size = 0.5

gear_body = Cylinder(gear_root_radius, gear_thickness)

tooth = Pos(gear_root_radius + tooth_height/2, 0, gear_thickness/2) * Box(tooth_width, tooth_height, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter/2, gear_thickness)

keyway = Pos(0, 0, gear_thickness - keyway_depth/2) * Box(keyway_width, gear_thickness, keyway_depth)
gear_body = gear_body - keyway

top_face = gear_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
gear_body = chamfer(top_edges, chamfer_size)

part = gear_body
part.name = "gear"
export_step(part, "output.step")