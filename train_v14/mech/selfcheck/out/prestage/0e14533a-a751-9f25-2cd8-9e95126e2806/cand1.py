from build123d import *

block_width = 80.0
block_depth = 50.0
block_height = 60.0
bore_radius = 8.0
bore_depth = 40.0
countersink_radius = 12.0
countersink_depth = 10.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_radius = 3.0
mount_hole_spacing = 30.0
rib_width = 20.0
rib_height = 10.0
rib_thickness = 5.0

solid_body = Box(block_width, block_depth, block_height)

solid_body = solid_body - Pos(0, 0, block_height/2 - bore_depth/2) * Cylinder(bore_radius, bore_depth)
solid_body = solid_body - Pos(0, 0, block_height/2 - countersink_depth/2) * Cone(bore_radius, countersink_radius, countersink_depth)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_radius, block_depth)

solid_body = solid_body + Pos(0, block_depth/2 - rib_thickness/2, 0) * Box(rib_width, rib_thickness, rib_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(front_face.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_bore_and_rib"
export_step(part, "output.step")