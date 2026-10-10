from build123d import *
import math

gear_base_radius = 30.0
gear_thickness = 10.0
num_teeth = 20
tooth_height = 6.0
tooth_width = 8.0
central_hole_diameter = 6.0
chamfer_distance = 0.5

base = Cylinder(gear_base_radius, gear_thickness)

tooth = Pos(gear_base_radius + tooth_height / 2, 0, gear_thickness / 2) * Box(tooth_width, tooth_height, gear_thickness)

gear = base
for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear = gear + Rot(0, 0, angle) * tooth

gear = gear - Cylinder(central_hole_diameter / 2, gear_thickness * 2)

vertical_edges = gear.edges().filter_by(Axis.Z)
gear = chamfer(vertical_edges, chamfer_distance)

part = gear
part.name = "gear"
export_step(part, "output.step")