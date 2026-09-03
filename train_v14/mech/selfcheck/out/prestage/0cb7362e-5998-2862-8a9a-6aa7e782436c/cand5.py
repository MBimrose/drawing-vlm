from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 10.0
rib_height = 4.0
rib_width = 20.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 5.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
set_screw_offset = 4.0
chamfer_size = 1.0

base = Pos(0, 0, jaw_thickness/2) * Box(jaw_length, jaw_width, jaw_thickness)
rib = Pos(0, 0, jaw_thickness/2) * Box(rib_width, jaw_width, rib_height)
pocket = Pos(0, 0, jaw_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = base + rib - pocket

hole_center_x = jaw_length/2 - set_screw_offset
shaft_hole = Pos(hole_center_x, 0, jaw_thickness/2) * Cylinder(set_screw_diameter/2, jaw_thickness + 10)
cbore_hole = Pos(hole_center_x, 0, set_screw_head_depth/2) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)
solid_body = solid_body - shaft_hole - cbore_hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "jaw_with_rib_pocket_and_setscrew"
export_step(part, "output.step")