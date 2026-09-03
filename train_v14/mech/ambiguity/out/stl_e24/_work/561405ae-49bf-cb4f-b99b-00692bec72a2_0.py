from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_offset_x = 0.0
pocket_offset_y = -10.0
fillet_radius = 4.0
chamfer_distance = 2.0
hole_diameter = 6.0
hole_spacing = 30.0
hole_offset_y = 15.0
rib_thickness = 4.0
rib_height = 8.0
rib_offset_y = 10.0
notch_diameter = 12.0
notch_offset_x = -20.0
notch_offset_y = -10.0

solid_body = Box(block_length, block_width, block_height)

pocket = Pos(pocket_offset_x, pocket_offset_y, pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

notch = Pos(notch_offset_x, notch_offset_y, 0) * Cylinder(notch_diameter/2, block_height)
solid_body = solid_body - notch

hole_positions = [
    (-hole_spacing/2, hole_offset_y),
    (hole_spacing/2, hole_offset_y),
    (-hole_spacing/2, -hole_offset_y),
    (hole_spacing/2, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

rib = Pos(0, rib_offset_y, rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "block_with_pocket_notch_holes_rib"
export_step(part, "output.step")