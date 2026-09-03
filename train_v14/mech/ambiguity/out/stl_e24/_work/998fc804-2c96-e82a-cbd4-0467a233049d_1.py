from build123d import *

bracket_length = 100.0
bracket_width = 60.0
bracket_thickness = 16.0
wall_thickness = 2.0
slot_width = 20.0
slot_height = 8.0
hole_diameter = 6.0
hole_count = 5
hole_margin = 10.0
rib_width = 8.0
rib_height = 4.0
chamfer_size = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, bracket_width/2 - wall_thickness/2, 0) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_cut

hole_spacing = (bracket_width - 2 * hole_margin) / (hole_count - 1)
for i in range(hole_count):
    y_pos = -bracket_width/2 + hole_margin + i * hole_spacing
    hole = Pos(-bracket_length/2 + hole_margin, y_pos, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)
    solid_body = solid_body - hole

rib = Pos(-bracket_length/2 + rib_width/2, 0, bracket_thickness/2 - rib_height/2) * Box(rib_width, bracket_width - 2*wall_thickness, rib_height)
solid_body = solid_body + rib

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")