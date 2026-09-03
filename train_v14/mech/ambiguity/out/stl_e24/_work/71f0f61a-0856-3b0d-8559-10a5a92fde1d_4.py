from build123d import *

block_length = 70
block_width = 40
block_height = 20
central_hole_diameter = 15
slot_width = 8
slot_depth = 10
fillet_radius = 2
chamfer_distance = 0.5
mount_hole_diameter = 5
mount_hole_offset = 5
rib_width = 10
rib_height = 5
rib_thickness = 2

solid_body = Box(block_length, block_width, block_height)

# Central through hole
solid_body = solid_body - Cylinder(central_hole_diameter/2, block_height)

# Slot cut from >X face
slot_box = Pos(block_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, block_width, slot_width)
solid_body = solid_body - slot_box

# Fillet vertical edges
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

# Mount holes at 4 corners
for x, y in [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)
]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

# Rib on bottom face
rib = Pos(0, 0, -block_height/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

# Chamfer top and bottom edges
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(top_face.edges() + bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "block_with_holes_slot_rib"
export_step(part, "output.step")