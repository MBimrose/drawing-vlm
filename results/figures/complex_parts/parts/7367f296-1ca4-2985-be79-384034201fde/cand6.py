from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 10.0
gear_thickness = 10.0
tooth_width = 4.0
tooth_height = 5.0
tooth_count = 12
central_hole_diameter = 10.0
chamfer_distance = 0.5

base = Cylinder(gear_outer_radius, gear_thickness)

tooth = Pos(gear_inner_radius + tooth_height / 2, 0, gear_thickness / 2) * Box(tooth_width, tooth_height, gear_thickness)

gear = base
for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    gear = gear + Rot(0, 0, angle) * tooth

gear = gear - Cylinder(central_hole_diameter / 2, gear_thickness)

vertical_edges = gear.edges().filter_by(Axis.Z)
gear = chamfer(vertical_edges, chamfer_distance)

part = gear
part.name = "gear"
export_step(part, "output.step")