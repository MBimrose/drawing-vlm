from build123d import *

block_width = 70.0
block_depth = 40.0
block_height = 12.0
corner_fillet_radius = 4.0
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = block_width / 4.0
notch_width = 10.0
notch_depth = 8.0
chamfer_distance = 0.8

solid_body = Box(block_width, block_depth, block_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
top_vertical_edges = vertical_edges.sort_by(Axis.Y)[-2:]
solid_body = fillet(top_vertical_edges, corner_fillet_radius)

notch_box = Pos(block_width/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, notch_depth)
solid_body = solid_body - notch_box

for i in range(3):
    x = (i - 1) * hole_spacing
    hole = Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_x_edges = bottom_face.edges().filter_by(Axis.X)
solid_body = chamfer(bottom_x_edges, chamfer_distance)

part = solid_body
part.name = "block_with_notch_holes_and_chamfer"
export_step(part, "output.step")