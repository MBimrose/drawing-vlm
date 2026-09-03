from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_height = 12.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 6.0
fillet_radius = 1.5
chamfer_distance = 1.0
set_screw_diameter = 4.0
set_screw_depth = 6.0
rib_height = 4.0
rib_width = 6.0
rib_offset = 5.0

solid_body = Box(knob_length, knob_width, knob_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, knob_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(knob_length/2 - set_screw_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole

rib = Pos(0, knob_width/2 - rib_offset - rib_width/2, rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "knob"
export_step(part, "output.step")