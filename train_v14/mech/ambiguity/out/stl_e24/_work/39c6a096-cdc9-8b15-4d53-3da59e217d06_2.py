from build123d import *
import math

block_length = 60.0
block_width = 40.0
block_height = 20.0
corner_radius = 3.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = 8.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 2
rib_width = 8.0
rib_length = block_length - 10.0
rib_height = 2.0
side_hole_diameter = 4.0
side_hole_spacing = 15.0
side_hole_offset = 10.0
countersink_diameter = 6.0
countersink_angle = 45.0
countersink_depth = (countersink_diameter - side_hole_diameter) / (2 * math.tan(math.radians(countersink_angle / 2)))

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), corner_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

for i in range(2):
    y = side_hole_offset + (i - 0.5) * side_hole_spacing
    z = 0
    shaft = Pos(0, y, z) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, block_length)
    solid_body = solid_body - shaft
    csink = Pos(block_length/2 - countersink_depth/2, y, z) * Rot(0, 90, 0) * Cone(side_hole_diameter/2, countersink_diameter/2, countersink_depth)
    solid_body = solid_body - csink

part = solid_body
part.name = "block_with_pocket_holes_rib"
export_step(part, "output.step")