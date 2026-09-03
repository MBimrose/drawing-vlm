from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 8.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 2
rib_width = 8.0
rib_length = 50.0
rib_height = 2.0
side_hole_diameter = 4.0
side_hole_spacing = 10.0
side_hole_rows = 2
countersink_diameter = 6.0
countersink_angle = 45.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = fillet(solid_body.faces().sort_by(Axis.Z)[0].edges(), fillet_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

for j in range(side_hole_rows):
    z = (j - (side_hole_rows-1)/2) * side_hole_spacing
    solid_body = solid_body - Pos(block_length/2, block_width/2 - 5, z) * Rot(0, 90, 0) * CounterSinkHole(side_hole_diameter/2, countersink_diameter/2, block_length + 10, countersink_angle)

part = solid_body
part.name = "block_with_pocket_rib_holes"
export_step(part, "output.step")