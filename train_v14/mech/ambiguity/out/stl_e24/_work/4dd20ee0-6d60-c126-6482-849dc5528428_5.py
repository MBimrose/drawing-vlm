from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 8.0
fillet_radius = 2.0
pin_hole_diameter = 5.0
pin_hole_offset = 25.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
rib_height = 3.0
rib_width = 6.0
rib_thickness = 2.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
counterbore_spacing = 20.0
counterbore_offset = 15.0

solid_body = Box(leaf_length, leaf_width, leaf_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pin_x = -leaf_length/2 + pin_hole_offset
solid_body = solid_body - Pos(pin_x, 0, 0) * Cylinder(pin_hole_diameter/2, leaf_thickness * 2)

pocket_z = leaf_thickness/2 - pocket_depth/2
solid_body = solid_body - Pos(0, 0, pocket_z) * Box(pocket_length, pocket_width, pocket_depth)

rib_z = -leaf_thickness/2 - rib_height/2
solid_body = solid_body + Pos(0, 0, rib_z) * Box(rib_width, rib_thickness, rib_height)

cb_x = -leaf_length/2 + counterbore_offset
for y in [-counterbore_spacing/2, counterbore_spacing/2]:
    cb_z = -leaf_thickness/2 + counterbore_depth/2
    solid_body = solid_body - Pos(cb_x, y, cb_z) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid_body
part.name = "leaf_with_rib_and_holes"
export_step(part, "output.step")