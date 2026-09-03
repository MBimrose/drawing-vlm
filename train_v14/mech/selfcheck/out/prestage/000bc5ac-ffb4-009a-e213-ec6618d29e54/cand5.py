from build123d import *

bracket_length = 60.0
bracket_width = 40.0
bracket_thickness = 8.0
wall_thickness = 2.0
slot_width = 15.0
slot_length = 20.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Box(wall_thickness * 2, slot_width, slot_length)
slot_box = Pos(bracket_length/2 - wall_thickness, 0, 0) * slot_box
solid_body = solid_body - slot_box

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Cylinder(hole_diameter/2, bracket_thickness + 1)
    hole = Pos(x, 0, 0) * hole
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")