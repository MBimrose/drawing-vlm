from build123d import *

base_radius = 30.0
base_thickness = 15.0
tooth_height = 8.0
tooth_width = 6.0
num_teeth = 20
central_hole_diameter = 6.0

base = Cylinder(base_radius, base_thickness)
tooth = Pos(base_radius + tooth_height/2, 0, base_thickness/2) * Box(tooth_height, tooth_width, base_thickness)

gear = base
for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear = gear + Rot(0, 0, angle) * tooth

gear = gear - Cylinder(central_hole_diameter/2, base_thickness)

part = gear
part.name = "gear"
export_step(part, "output.step")