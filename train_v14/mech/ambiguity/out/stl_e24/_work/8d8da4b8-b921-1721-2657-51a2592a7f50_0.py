from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 25.0
slot_width = 6.0
slot_offset = 15.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
rib_height = 2.0
rib_width = 10.0
rib_length = plate_length - 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

slot1 = Pos(0, slot_offset, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_offset, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot1 - slot2

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness)

rib = Pos(0, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_slots_holes_rib"
export_step(part, "output.step")