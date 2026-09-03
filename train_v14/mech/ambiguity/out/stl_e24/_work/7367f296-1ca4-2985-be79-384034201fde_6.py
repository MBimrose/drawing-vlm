from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 15.0
gear_thickness = 10.0
bore_diameter = 10.0
tooth_height = 4.0
tooth_width = 5.0
tooth_count = 12
keyway_width = 2.0
keyway_depth = 6.0
chamfer_distance = 0.5

gear_body = Cylinder(gear_outer_radius, gear_thickness)
gear_body = gear_body - Cylinder(bore_diameter/2, gear_thickness)

tooth = Pos(gear_inner_radius + tooth_height/2, 0, gear_thickness/2) * Box(tooth_width, tooth_height, gear_thickness)

teeth = tooth
for i in range(1, tooth_count):
    angle = i * 360.0 / tooth_count
    teeth = teeth + Rot(0, 0, angle) * tooth

gear_with_teeth = gear_body + teeth

keyway = Pos(bore_diameter/2 + keyway_depth/2, 0, gear_thickness/2) * Box(keyway_width, keyway_depth, gear_thickness)

gear_with_keyway = gear_with_teeth - keyway

vertical_edges = gear_with_keyway.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "gear_with_teeth_and_keyway"
export_step(part, "output.step")