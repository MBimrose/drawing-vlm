from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
fillet_radius = 3.0
chamfer_distance = 1.0
hole_diameter = 10.0
hole_depth = 10.0
hole_spacing = 30.0
rib_height = 5.0
rib_width = 5.0
rib_length = 20.0
notch_width = 10.0
notch_height = 10.0
notch_depth = 5.0

solid_body = Box(block_length, block_width, block_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

notch = Pos(-block_length/2 + notch_depth/2, 0, block_height/2) * Box(notch_depth, notch_width, notch_height)
solid_body = solid_body - notch

rib = Pos(0, 0, block_height + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    hole = Pos(x, y, block_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "block_with_notch_rib_and_holes"
export_step(part, "output.step")