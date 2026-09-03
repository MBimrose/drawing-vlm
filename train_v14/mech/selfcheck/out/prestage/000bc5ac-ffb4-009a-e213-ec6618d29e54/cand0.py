from build123d import *

bracket_width = 60.0
bracket_depth = 40.0
bracket_thickness = 8.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 15.0
hole_diameter = 5.0
hole_spacing = 30.0
fillet_radius = 0.5

solid_body = Box(bracket_width, bracket_depth, bracket_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(bracket_width/2 - wall_thickness/2, 0, 0) * Box(wall_thickness, slot_width, slot_height)
solid_body = solid_body - slot_cut

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness + 1)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")