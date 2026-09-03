from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
groove_width = 6.0
groove_depth = 4.0
groove_height = 12.0
groove_offset_from_top = 5.0
hole_diameter = 5.0
hole_offset_from_left = 30.0
hole_offset_from_bottom = 4.0
rib_width = 12.0
rib_thickness = 2.0
rib_height = 4.0
chamfer_size = 0.8

result = Box(jaw_length, jaw_width, jaw_thickness)

groove_cut = Pos(jaw_length/2 - groove_depth/2, groove_offset_from_top + groove_width/2, 0) * Box(groove_depth, groove_width, groove_height)
result = result - groove_cut

hole_x = -jaw_length/2 + hole_offset_from_left
hole_z = -jaw_thickness/2 + hole_offset_from_bottom
hole = Pos(hole_x, -jaw_width/2 + jaw_thickness/2, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, jaw_thickness)
result = result - hole

rib = Pos(0, 0, jaw_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = result + rib

part = result
part.name = "jaw_with_groove_hole_rib"
export_step(part, "output.step")