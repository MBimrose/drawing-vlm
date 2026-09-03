from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
cavity_width = outer_width - 2 * wall_thickness
cavity_height = outer_depth - 2 * wall_thickness
knob_diameter = 12.0
knob_offset_z = 10.0
relief_width = 6.0
relief_depth = 4.0
relief_offset_z = 12.0
chamfer_size = 1.0

base = Box(outer_width, outer_depth, outer_height)
cavity = Box(cavity_width, cavity_height, outer_height)
result = base - cavity

hole = Pos(outer_width/2, 0, knob_offset_z) * Rot(0, 90, 0) * Cylinder(knob_diameter/2, outer_width * 2)
result = result - hole

relief = Pos(-outer_width/2 + wall_thickness/2, 0, relief_offset_z) * Box(relief_width, wall_thickness, relief_depth)
result = result - relief

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "knob_housing"
export_step(part, "output.step")