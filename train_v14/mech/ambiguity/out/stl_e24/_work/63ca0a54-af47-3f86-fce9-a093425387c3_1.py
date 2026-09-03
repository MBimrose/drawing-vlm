from build123d import *

knob_length = 70.0
knob_width = 30.0
knob_height = 12.0
wall_thickness = 2.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 12.0
fillet_radius = 1.5
chamfer_distance = 1.0
hole_diameter = 4.0
hole_depth = 6.0

solid_body = Box(knob_length, knob_width, knob_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

num_ribs = int((knob_length - 2 * wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_pos = -knob_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, -knob_height/2 + rib_height/2) * Box(rib_width, knob_width - 2 * wall_thickness, rib_height)
    solid_body = solid_body + rib

hole = Pos(knob_length/2 - hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "knob"
export_step(part, "output.step")