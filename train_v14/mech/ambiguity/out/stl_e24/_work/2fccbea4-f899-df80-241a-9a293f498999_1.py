from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 8.0
slot_length = 30.0
slot_width = 6.0
slot_spacing = 15.0
num_slots = 4
chamfer_dist = 0.8
mount_hole_dia = 5.0
mount_hole_offset = 10.0
rib_height = 4.0
rib_width = 6.0
rib_length = 30.0
rib_spacing = 15.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
solid_body = p.part

slot_y_start = -((num_slots - 1) * slot_spacing) / 2
for i in range(num_slots):
    y = slot_y_start + i * slot_spacing
    solid_body = solid_body - Pos(0, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness)

rib_y_start = -((num_slots - 1) * rib_spacing) / 2
for i in range(num_slots):
    y = rib_y_start + i * rib_spacing
    solid_body = solid_body + Pos(0, y, rib_height/2) * Box(rib_length, rib_width, rib_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "plate_with_slots_ribs"
export_step(part, "output.step")