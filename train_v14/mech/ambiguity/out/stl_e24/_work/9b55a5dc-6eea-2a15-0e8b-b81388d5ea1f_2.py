from build123d import *

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
bearing_diameter = 30.0
bearing_depth = 6.0
bearing_fillet_radius = 3.0
corner_hole_diameter = 4.0
corner_hole_offset = 15.0
counterbore_diameter = 6.0
counterbore_depth = 4.0
top_chamfer = 0.8

solid_body = Box(block_length, block_width, block_thickness)

bearing_hole = Pos(0, 0, block_thickness/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
solid_body = solid_body - bearing_hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, bearing_fillet_radius)

hole_positions = [
    (-block_length/2 + corner_hole_offset, -block_width/2 + corner_hole_offset),
    ( block_length/2 - corner_hole_offset, -block_width/2 + corner_hole_offset),
    ( block_length/2 - corner_hole_offset,  block_width/2 - corner_hole_offset),
    (-block_length/2 + corner_hole_offset,  block_width/2 - corner_hole_offset)
]

for x, y in hole_positions:
    cbore = Pos(x, y, block_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    shaft = Pos(x, y, 0) * Cylinder(corner_hole_diameter/2, block_thickness)
    solid_body = solid_body - cbore - shaft

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, top_chamfer)

part = solid_body
part.name = "bearing_block"
export_step(part, "output.step")