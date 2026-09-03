from build123d import *

plate_size = 80.0
plate_thickness = 5.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
central_cutout_width = 12.0
central_cutout_height = 12.0
slot_width = 8.0
slot_length = 30.0
boss_diameter = 20.0
boss_height = 3.0
chamfer_distance = 2.0
fillet_radius = 0.5

solid_body = Box(plate_size, plate_size, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (-plate_size/2 + corner_hole_offset, -plate_size/2 + corner_hole_offset),
    ( plate_size/2 - corner_hole_offset, -plate_size/2 + corner_hole_offset),
    ( plate_size/2 - corner_hole_offset,  plate_size/2 - corner_hole_offset),
    (-plate_size/2 + corner_hole_offset,  plate_size/2 - corner_hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, plate_thickness)

solid_body = solid_body - Box(central_cutout_width, central_cutout_height, plate_thickness)

slot_offsets = [
    (0,  plate_size/2 - slot_length/2 - corner_hole_offset),
    (0, -plate_size/2 + slot_length/2 + corner_hole_offset),
    ( plate_size/2 - slot_length/2 - corner_hole_offset, 0),
    (-plate_size/2 + slot_length/2 + corner_hole_offset, 0)
]
for x, y in slot_offsets:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_width, slot_length, plate_thickness)

solid_body = solid_body + Pos(0, 0, plate_thickness/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")