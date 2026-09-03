from build123d import *

block_length = 80
block_width = 50
block_height = 30
fillet_radius = 4
chamfer_distance = 2
hole_diameter = 6
hole_spacing_x = 30
hole_spacing_y = 30
hole_rows = 2
hole_cols = 2
pocket_length = 40
pocket_width = 30
pocket_depth = 10
rib_thickness = 5
rib_height = 10
slot_length = 30
slot_width = 10
slot_offset = 15
circle_cut_diameter = 12
circle_cut_offset_x = -20
circle_cut_offset_y = 0

solid = Box(block_length, block_width, block_height)
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_distance)

solid = solid - Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid + Pos(0, block_width/2 - rib_thickness/2, 0) * Box(block_length, rib_thickness, rib_height)
solid = solid - Pos(-block_length/2 + slot_offset, 0, 0) * Box(slot_length, block_width, slot_width)
solid = solid - Pos(circle_cut_offset_x, circle_cut_offset_y, 0) * Cylinder(circle_cut_diameter/2, block_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

part = solid
part.name = "block_with_features"
export_step(part, "output.step")