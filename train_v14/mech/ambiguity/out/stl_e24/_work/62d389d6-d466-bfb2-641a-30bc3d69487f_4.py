from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
tab_length = 30.0
tab_width = 12.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 20.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_distance = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_width/2, 0) * Box(tab_length, tab_width, bracket_thickness)
solid_body = base + tab

slot1 = Pos(-slot_spacing/2, 0, 0) * Box(slot_width, slot_length, bracket_thickness)
slot2 = Pos(slot_spacing/2, 0, 0) * Box(slot_width, slot_length, bracket_thickness)
solid_body = solid_body - slot1 - slot2

hole1 = Pos(-hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_width + 10)
hole2 = Pos(hole_spacing/2, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, bracket_width + 10)
solid_body = solid_body - hole1 - hole2

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")