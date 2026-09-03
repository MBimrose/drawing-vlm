from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 10.0
recess_radius = 8.0
recess_depth = 4.0
through_hole_diameter = 4.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
slot_width = 10.0
slot_depth = 5.0
fillet_radius = 2.0
chamfer_distance = 2.0

result = Box(plate_length, plate_width, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result - Pos(0, 0, plate_thickness/2 + boss_height - recess_depth/2) * Cylinder(recess_radius, recess_depth)
result = result - Pos(0, 0, boss_height/2) * Cylinder(through_hole_diameter/2, plate_thickness + boss_height)

corner_pts = [
    (-plate_length/2 + corner_hole_offset, -plate_width/2 + corner_hole_offset),
    ( plate_length/2 - corner_hole_offset, -plate_width/2 + corner_hole_offset),
    ( plate_length/2 - corner_hole_offset,  plate_width/2 - corner_hole_offset),
    (-plate_length/2 + corner_hole_offset,  plate_width/2 - corner_hole_offset)
]
for x, y in corner_pts:
    result = result - Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)

result = result - Pos(0, plate_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, plate_thickness)
result = result - Pos(0, -plate_width/2 + slot_depth/2, 0) * Box(slot_width, slot_depth, plate_thickness)
result = result - Pos(plate_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, plate_thickness)
result = result - Pos(-plate_length/2 + slot_depth/2, 0, 0) * Box(slot_depth, slot_width, plate_thickness)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)
top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "plate_with_boss"
export_step(part, "output.step")