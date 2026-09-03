from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_thickness = 12.0
wall_thickness = 2.0
rib_height = 4.0
rib_width = 6.0
rib_length = knob_length - 2 * wall_thickness
fillet_radius = 1.5
chamfer_distance = 1.0
blind_hole_diameter = 4.0
blind_hole_depth = 6.0

base = Box(knob_length, knob_width, knob_thickness)
rib_top = Pos(0, 0, knob_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
rib_bottom = Pos(0, 0, -knob_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = base + rib_top + rib_bottom

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

hole = Pos(knob_length/2 - blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "knob_with_ribs"
export_step(part, "output.step")