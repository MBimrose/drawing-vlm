from build123d import *
import math

gear_base_radius = 30.0
gear_thickness = 10.0
tooth_height = 8.0
tooth_width = 6.0
num_teeth = 20
chamfer_distance = 2.0
central_hole_diameter = 6.0

gear_body = Cylinder(gear_base_radius, gear_thickness)
top_face = gear_body.faces().sort_by(Axis.Z)[-1]
gear_body = chamfer(top_face.edges(), chamfer_distance)

tooth = Pos(gear_base_radius + tooth_height/2, 0, gear_thickness/2) * Box(tooth_height, tooth_width, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter/2, gear_thickness * 2)

part = gear_body
part.name = "gear"
export_step(part, "output.step")