from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_height = 12.0
wall_thickness = 2.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 10.0
set_screw_diameter = 4.0
set_screw_depth = 6.0
fillet_radius = 1.5
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(knob_length, knob_width)
    extrude(amount=knob_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

num_ribs = int((knob_length - 2 * wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_offset = -knob_length / 2 + wall_thickness + rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_offset, 0, rib_height / 2) * Box(rib_width, knob_width - 2 * wall_thickness, rib_height)
    solid_body = solid_body + rib

hole = Pos(knob_length / 2 - set_screw_depth / 2, 0, knob_height / 2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, set_screw_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")