from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_height = 12.0
wall_thickness = 2.0
pocket_depth = 4.0
pocket_margin = 4.0
fillet_radius = 1.5
chamfer_distance = 1.0
set_screw_diameter = 4.0
set_screw_depth = 6.0
set_screw_offset_from_end = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(knob_length, knob_width)
    extrude(amount=knob_height)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

pocket_w = knob_length - 2 * pocket_margin
pocket_h = knob_width - 2 * pocket_margin
pocket_box = Pos(0, 0, knob_height - pocket_depth / 2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket_box

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

screw_x = knob_length / 2 - set_screw_offset_from_end
screw_hole = Pos(screw_x, 0, knob_height / 2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, set_screw_depth)
solid_body = solid_body - screw_hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")