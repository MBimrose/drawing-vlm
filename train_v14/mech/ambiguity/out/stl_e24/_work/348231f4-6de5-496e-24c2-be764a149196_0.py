from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 3.0
rib_width = 5.0
rib_height = leaf_thickness
hole_diameter = 2.0
cbore_diameter = 4.0
cbore_depth = 2.0

base = Box(leaf_length, leaf_width, leaf_thickness)
left_rib = Pos(-leaf_length/2 + rib_width/2, 0, 0) * Box(rib_width, leaf_width, rib_height)
right_rib = Pos(leaf_length/2 - rib_width/2, 0, 0) * Box(rib_width, leaf_width, rib_height)

solid_body = base + left_rib + right_rib

shaft = Cylinder(hole_diameter/2, leaf_thickness + 1)
cbore = Pos(0, 0, leaf_thickness/2 - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
solid_body = solid_body - shaft - cbore

part = solid_body
part.name = "leaf_with_ribs_and_cbore"
export_step(part, "output.step")