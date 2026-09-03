from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
rib_width = 10.0
rib_height = 5.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
countersink_diameter = 10.0
countersink_angle = 90.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

# Cut slot through top face
slot = Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)
solid_body = solid_body - slot

# Add rib on bottom face
rib = Pos(0, 0, rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body + rib

# Chamfer vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

# Counterbore holes at 4 corners
hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset)
]

for x, y in hole_positions:
    hole = Pos(x, y, 0) * CounterBoreHole(mount_hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_slot_rib_and_holes"
export_step(part, "output.step")