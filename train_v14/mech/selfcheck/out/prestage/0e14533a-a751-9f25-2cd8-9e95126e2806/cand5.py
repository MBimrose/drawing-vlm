from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 60.0
bore_diameter = 16.0
countersink_diameter = 24.0
countersink_angle = 30.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_height = 5.0
rib_width = 10.0
rib_length = block_length - 20.0

solid_body = Box(block_length, block_width, block_height)

csk_depth = (countersink_diameter/2 - bore_diameter/2) / math.tan(math.radians(countersink_angle/2))
bore_cyl = Pos(0, 0, block_height/2 - (block_height - csk_depth)/2) * Cylinder(bore_diameter/2, block_height - csk_depth)
csk_cone = Pos(0, 0, block_height/2 - csk_depth/2) * Cone(bore_diameter/2, countersink_diameter/2, csk_depth)
solid_body = solid_body - (bore_cyl + csk_cone)

top_z_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-2:]
solid_body = fillet(top_z_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, block_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)
    solid_body = solid_body - hole

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "block_with_bore_and_rib"
export_step(part, "output.step")