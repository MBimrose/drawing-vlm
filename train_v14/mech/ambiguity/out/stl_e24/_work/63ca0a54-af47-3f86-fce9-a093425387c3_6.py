from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_height = 12.0
wall_thickness = 2.0
slot_width = 15.0
slot_depth = knob_height - wall_thickness
blind_hole_diameter = 4.0
blind_hole_depth = 6.0
fillet_radius = 1.5
chamfer_distance = 1.0

solid_body = Box(knob_length, knob_width, knob_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

slot_box = Pos(0, 0, knob_height - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
solid_body = solid_body - slot_box

hole_cyl = Pos(knob_length/2 - blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "knob"
export_step(part, "output.step")