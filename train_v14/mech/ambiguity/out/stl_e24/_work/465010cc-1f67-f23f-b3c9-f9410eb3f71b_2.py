from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
corner_radius = 5.0
slot_length = 40.0
slot_width = 8.0
slot_spacing = 20.0
mount_hole_dia = 6.0
mount_hole_offset = 10.0
rib_height = 4.0
rib_thickness = 2.0
chamfer_dist = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_thickness)

solid_body = p.part

# Fillet top-right corner edge (parallel to Z, max X and Y)
z_edges = solid_body.edges().filter_by(Axis.Z)
corner_edge = z_edges.sort_by(Axis.X)[-2:].sort_by(Axis.Y)[-1:]
solid_body = fillet(corner_edge, corner_radius)

# Cut two slots through the block
slot_y_positions = [-slot_spacing/2, slot_spacing/2]
for y in slot_y_positions:
    slot = Pos(0, y, block_thickness/2) * Box(slot_length, slot_width, block_thickness)
    solid_body = solid_body - slot

# Chamfer all vertical edges
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_dist)

# Mount holes at four corners
hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, block_thickness/2) * Cylinder(mount_hole_dia/2, block_thickness)
    solid_body = solid_body - hole

# Rib on bottom face
rib = Pos(0, 0, rib_height/2) * Box(rib_thickness, block_width - 2*mount_hole_offset, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_slots_ribs"
export_step(part, "output.step")