from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 10.0
gear_thickness = 10.0
hub_height = 5.0
tooth_height = 8.0
tooth_width = 6.0
num_teeth = 20
central_hole_diameter = 6.0
chamfer_size = 0.5

base = Cylinder(gear_outer_radius, gear_thickness)
hub = Pos(0, 0, gear_thickness/2 + hub_height/2) * Cylinder(gear_inner_radius, hub_height)
gear_body = base + hub

tooth = Pos(gear_outer_radius + tooth_height/2, 0, gear_thickness/2) * Box(tooth_height, tooth_width, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter/2, gear_thickness + hub_height + 10)

vertical_edges = gear_body.edges().filter_by(Axis.Z)
gear_body = chamfer(vertical_edges, chamfer_size)

part = gear_body
part.name = "gear"
export_step(part, "output.step")