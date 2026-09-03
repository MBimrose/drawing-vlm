from build123d import *
import math

block_length = 60.0
block_width = 40.0
block_height = 20.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 2
rib_width = 8.0
rib_length = 50.0
rib_height = 4.0
pocket_depth = 8.0
pocket_margin = 5.0
csk_hole_diameter = 4.0
csk_countersink_diameter = 6.0
csk_angle = 45.0
csk_depth = 5.0
csk_spacing = 10.0
csk_rows = 2

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = fillet(solid_body.faces().sort_by(Axis.Z)[0].edges(), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, block_height + 1)

rib = Pos(0, 0, block_height / 2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, block_height / 2 - pocket_depth / 2) * Box(block_length - 2 * pocket_margin, block_width - 2 * pocket_margin, pocket_depth)
solid_body = solid_body - pocket

for i in range(csk_rows):
    y = (i - (csk_rows - 1) / 2) * csk_spacing
    z = block_height / 4
    csk_hole = CounterSinkHole(csk_hole_diameter / 2, csk_countersink_diameter / 2, csk_depth, csk_angle)
    solid_body = solid_body - Pos(block_length / 2, y, z) * Rot(0, -90, 0) * csk_hole

part = solid_body
part.name = "block_with_holes_rib_pocket"
export_step(part, "output.step")