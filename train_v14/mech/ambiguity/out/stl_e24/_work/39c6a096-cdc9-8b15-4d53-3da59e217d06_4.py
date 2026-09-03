from build123d import *

block_width = 60.0
block_depth = 40.0
block_height = 20.0
fillet_radius = 3.0
pocket_margin = 5.0
pocket_depth = 8.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_rows = 2
hole_cols = 2
rib_width = 8.0
rib_height = 2.0
rib_length = block_width - 2 * pocket_margin
side_hole_diameter = 4.0
side_hole_csk_diameter = 6.0
side_hole_csk_angle = 45.0
side_hole_spacing = 15.0
side_hole_offset = 10.0

with BuildPart() as p:
    Box(block_width, block_depth, block_height)
solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_w = block_width - 2 * pocket_margin
pocket_d = block_depth - 2 * pocket_margin
pocket_cut = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_w, pocket_d, pocket_depth)
solid_body = solid_body - pocket_cut

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 10)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

for i in range(2):
    y_pos = side_hole_offset + i * side_hole_spacing
    csk = Pos(block_width/2, y_pos, 0) * Rot(0, 90, 0) * CounterSinkHole(side_hole_diameter/2, side_hole_csk_diameter/2, side_hole_csk_angle)
    solid_body = solid_body - csk

part = solid_body
part.name = "block_with_pocket_holes_rib"
export_step(part, "output.step")