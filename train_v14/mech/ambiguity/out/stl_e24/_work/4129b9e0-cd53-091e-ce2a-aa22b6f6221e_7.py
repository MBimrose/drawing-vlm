from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
pocket_width = 30.0
pocket_height = 15.0
pocket_depth = 8.0
hole_diameter = 10.0
hole_spacing = 30.0
fillet_radius = 3.0
chamfer_distance = 1.0
rib_width = 20.0
rib_height = 5.0
rib_thickness = 5.0

result = Box(block_length, block_width, block_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

pocket = Pos(-block_length/2 + pocket_depth/2, 0, block_height/2) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    result = result - Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height)

rib = Pos(0, 0, block_height + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = result + rib

part = result
part.name = "block_with_pocket_holes_and_rib"
export_step(part, "output.step")