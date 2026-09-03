from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 5.0
central_cutout_diameter = 20.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 15.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
chamfer_distance = 2.0
fillet_radius = 1.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
        Circle(central_cutout_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

slot_positions = [
    (0, slot_offset),
    (0, -slot_offset),
    (slot_offset, 0),
    (-slot_offset, 0),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness * 2)

corner_offsets = [
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
]
for x, y in corner_offsets:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, plate_thickness * 2)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib_positions = [
    (plate_width/2 - rib_width/2 - 5, plate_height/2 - rib_height/2 - 5),
    (-plate_width/2 + rib_width/2 + 5, plate_height/2 - rib_height/2 - 5),
    (-plate_width/2 + rib_width/2 + 5, -plate_height/2 + rib_height/2 + 5),
    (plate_width/2 - rib_width/2 - 5, -plate_height/2 + rib_height/2 + 5),
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

part = solid_body
part.name = "plate_with_slots_ribs"
export_step(part, "output.step")