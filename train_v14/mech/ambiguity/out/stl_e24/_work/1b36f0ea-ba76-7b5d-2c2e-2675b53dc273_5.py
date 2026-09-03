from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 8.0
rib_height = 2.0
rib_margin = 5.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 18.0
slot_count = 3
mount_hole_dia = 4.0
mount_hole_offset = 10.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

rib1 = Pos(0, 0, plate_thickness + rib_height/2) * Box(plate_length - 2*rib_margin, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_width - 2*rib_margin, rib_height)
solid_body = solid_body + rib1 + rib2

slot_positions = [((i - (slot_count - 1) / 2) * slot_spacing, 0) for i in range(slot_count)]
for x, y in slot_positions:
    slot = Pos(x, y, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)
    solid_body = solid_body - slot

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness)
    solid_body = solid_body - hole

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_ribs_slots_holes"
export_step(part, "output.step")