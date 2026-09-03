from build123d import *
import math

gear_outer_radius = 30.0
gear_thickness = 10.0
tooth_height = 4.0
tooth_width = 2.0
tooth_count = 12
central_hole_diameter = 10.0
chamfer_distance = 0.5

gear_body = Cylinder(gear_outer_radius, gear_thickness)

tooth = Pos(gear_outer_radius - tooth_height/2, 0, gear_thickness/2) * Box(tooth_width, tooth_height, gear_thickness)

teeth = tooth
for i in range(1, tooth_count):
    angle = i * 360.0 / tooth_count
    teeth = teeth + Rot(0, 0, angle) * tooth

gear_with_teeth = gear_body + teeth

gear_with_hole = gear_with_teeth - Cylinder(central_hole_diameter/2, gear_thickness * 2)

vertical_edges = gear_with_hole.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "gear"
export_step(part, "output.step")