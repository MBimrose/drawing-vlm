from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 8.0
central_hole_dia = 20.0
corner_padding = 10.0
cbore_radius = 3.0
cbore_outer = 6.0
cbore_depth = 4.0
rib_width = 40.0
rib_height = 4.0
slot_length = 20.0
slot_width = 4.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_dia/2, plate_thickness * 2)

corner_x = plate_width/2 - corner_padding
corner_y = plate_height/2 - corner_padding
for cx, cy in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    solid_body = solid_body - Pos(cx, cy, 0) * Cylinder(cbore_radius, plate_thickness * 2)
    solid_body = solid_body - Pos(cx, cy, plate_thickness/2 - cbore_depth/2) * Cylinder(cbore_outer, cbore_depth)

solid_body = solid_body + Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)

solid_body = solid_body - Pos(0, plate_height/2 - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness * 2)
solid_body = solid_body - Pos(0, -plate_height/2 + slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness * 2)
solid_body = solid_body - Pos(plate_width/2 - slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - Pos(-plate_width/2 + slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness * 2)

part = solid_body
part.name = "plate_with_rib_and_slots"
export_step(part, "output.step")