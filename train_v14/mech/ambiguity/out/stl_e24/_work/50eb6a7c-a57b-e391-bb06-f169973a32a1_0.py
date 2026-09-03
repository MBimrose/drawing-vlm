from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 12.0
notch_width = 10.0
notch_height = 8.0
notch_depth = 8.0
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = block_length / 4.0
fillet_radius = 4.0
chamfer_distance = 0.8
rib_thickness = 4.0
rib_height = 6.0
rib_offset = 5.0

solid_body = Box(block_length, block_width, block_height)

notch = Pos(block_length/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, notch_height)
solid_body = solid_body - notch

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, block_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

fillet_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = fillet(fillet_edges, fillet_radius)

chamfer_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2]
solid_body = chamfer(chamfer_edges, chamfer_distance)

rib = Pos(0, -block_width/2 + rib_offset + rib_thickness/2, -block_height/2 + rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "notched_block_with_holes_and_rib"
export_step(part, "output.step")