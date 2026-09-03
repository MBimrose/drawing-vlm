from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
counterbore_diameter = 16.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
corner_hole_diameter = 6.0
corner_hole_offset = 12.0
slot_width = 10.0
slot_depth = 5.0
fillet_radius = 2.0
chamfer_distance = 0.5

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result - Pos(0, 0, plate_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - Pos(0, 0, boss_height/2) * Cylinder(through_hole_diameter/2, plate_thickness + boss_height)

corner_positions = [
    (plate_length/2 - corner_hole_offset, plate_width/2 - corner_hole_offset),
    (-plate_length/2 + corner_hole_offset, plate_width/2 - corner_hole_offset),
    (-plate_length/2 + corner_hole_offset, -plate_width/2 + corner_hole_offset),
    (plate_length/2 - corner_hole_offset, -plate_width/2 + corner_hole_offset),
]
for x, y in corner_positions:
    result = result - Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)

slot_positions = [
    (0, plate_width/2 - slot_depth/2),
    (0, -plate_width/2 + slot_depth/2),
    (plate_length/2 - slot_depth/2, 0),
    (-plate_length/2 + slot_depth/2, 0),
]
for x, y in slot_positions:
    result = result - Pos(x, y, 0) * Box(slot_width, slot_depth, plate_thickness)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = fillet(top_edges, fillet_radius)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")