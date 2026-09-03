from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
central_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_width = 6.0
rib_height = 8.0
rib_spacing = 15.0
chamfer_size = 1.0

solid_body = Box(block_length, block_width, block_height)

solid_body = solid_body - Cylinder(central_hole_diameter/2, block_height)
solid_body = solid_body - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

mount_hole = Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
for x in [-block_length/2 + wall_thickness/2, block_length/2 - wall_thickness/2]:
    for z in [block_height/2 - mount_hole_offset, -block_height/2 + mount_hole_offset]:
        solid_body = solid_body - Pos(x, 0, z) * mount_hole

rib_count = int((block_length - 2 * wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x = -block_length/2 + wall_thickness + i * rib_spacing
    solid_body = solid_body + Pos(x, 0, -block_height/2 + rib_height/2) * Box(rib_width, block_width - 2*wall_thickness, rib_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = chamfer(solid_body.edges().sort_by(Axis.Z)[:4], chamfer_size)

part = solid_body
part.name = "block_with_holes_and_ribs"
export_step(part, "output.step")