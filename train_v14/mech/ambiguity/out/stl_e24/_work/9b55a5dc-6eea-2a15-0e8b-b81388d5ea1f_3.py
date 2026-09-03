from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
corner_fillet_radius = 3.0
central_recess_diameter = 30.0
central_recess_depth = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
mount_hole_cbore_diameter = 6.0
mount_hole_cbore_depth = 4.0
rib_thickness = 4.0
rib_height = 6.0
chamfer_size = 0.8

solid_body = Box(block_length, block_width, block_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = solid_body - Pos(0, 0, block_thickness/2 - central_recess_depth/2) * Cylinder(central_recess_diameter/2, central_recess_depth)

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_thickness)
    solid_body = solid_body - Pos(x, y, block_thickness/2 - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)

rib1 = Pos(0, 0, -block_thickness/2 + rib_height/2) * Box(rib_thickness, block_width, rib_height)
rib2 = Pos(0, 0, -block_thickness/2 + rib_height/2) * Box(block_length, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "block_with_recess_and_ribs"
export_step(part, "output.step")