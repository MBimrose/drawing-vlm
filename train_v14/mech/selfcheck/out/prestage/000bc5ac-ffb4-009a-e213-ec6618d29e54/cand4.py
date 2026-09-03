from build123d import *

bracket_width = 60.0
bracket_height = 40.0
bracket_thickness = 8.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 20.0
hole_diameter = 5.0
hole_spacing = 30.0

solid_body = Box(bracket_width, bracket_height, bracket_thickness)

inner_width = bracket_width - 2 * wall_thickness
inner_height = bracket_height - 2 * wall_thickness
inner_depth = bracket_thickness - wall_thickness
cavity = Pos(0, 0, bracket_thickness/2 - inner_depth/2) * Box(inner_width, inner_height, inner_depth)
solid_body = solid_body - cavity

slot = Pos(bracket_width/2 - wall_thickness/2, 0, 0) * Box(wall_thickness, slot_width, slot_height)
solid_body = solid_body - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")