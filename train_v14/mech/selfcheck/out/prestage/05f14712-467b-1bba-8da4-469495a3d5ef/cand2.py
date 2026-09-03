from build123d import *

block_length = 70
block_width = 50
block_height = 30
wall_thickness = 5
port_diameter = 12
port_spacing = 30
mount_hole_diameter = 4
mount_hole_offset = 10
fillet_radius = 1
chamfer_distance = 1
rib_thickness = 4
rib_height = 10
rib_spacing = 15
slot_width = 5
slot_length = 20
slot_offset = 10
pocket_width = 20
pocket_length = 30
pocket_depth = 8
side_hole_diameter = 6
side_hole_offset = 12

solid = Box(block_length, block_width, block_height)

for x in [-port_spacing/2, port_spacing/2]:
    solid = solid - Pos(x, 0, 0) * Cylinder(port_diameter/2, block_height)

for x in [-(block_length/2 - mount_hole_offset), (block_length/2 - mount_hole_offset)]:
    for y in [-(block_width/2 - mount_hole_offset), (block_width/2 - mount_hole_offset)]:
        solid = solid - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

solid = solid - Pos(0, 0, block_height/2 - slot_offset - slot_width/2) * Box(slot_length, slot_width, slot_width)
solid = solid - Pos(0, 0, block_height/2 - slot_offset - slot_width/2) * Box(block_length - 2*slot_offset, slot_width, slot_width)
solid = solid - Pos(-block_length/4, 0, -block_height/2 + pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid = solid - Pos(0, 0, side_hole_offset) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, block_length)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_distance)

part = solid
part.name = "block_with_features"
export_step(part, "output.step")