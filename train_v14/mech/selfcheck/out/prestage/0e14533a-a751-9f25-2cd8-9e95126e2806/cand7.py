from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 60.0
bore_diameter = 16.0
countersink_diameter = 24.0
countersink_depth = 8.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_thickness = 4.0
rib_width = 20.0
rib_height = 10.0

solid_body = Box(block_length, block_width, block_height)

csk_cone = Pos(0, 0, block_height/2 - countersink_depth/2) * Cone(bore_diameter/2, countersink_diameter/2, countersink_depth)
bore_cyl = Pos(0, 0, 0) * Cylinder(bore_diameter/2, block_height + 10)
solid_body = solid_body - csk_cone - bore_cyl

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)
    solid_body = solid_body - hole

rib = Pos(0, 0, block_height/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
vertical_edges = top_y_face.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "block_with_bore_and_mounts"
export_step(part, "output.step")