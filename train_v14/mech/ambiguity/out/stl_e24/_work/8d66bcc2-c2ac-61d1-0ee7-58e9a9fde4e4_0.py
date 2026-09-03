from build123d import *

outer_width = 50.0
outer_depth = 35.0
outer_height = 12.0
wall_thickness = 2.0
inner_width = 34.0
inner_depth = 20.0
inner_height = 8.0
fillet_radius = 2.0
notch_radius = 6.0
notch_offset_x = 15.0
notch_offset_y = 10.0
hole_diameter = 4.0
hole_offset_x = 10.0
hole_offset_y = 8.0

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
notch = Pos(notch_offset_x, notch_offset_y, outer_height/2) * Cylinder(notch_radius, outer_height)
base = base - notch

cavity = Pos(-inner_width/2, -inner_depth/2, wall_thickness + inner_height/2) * Box(inner_width, inner_depth, inner_height)
base = base - cavity

hole = Pos(hole_offset_x, hole_offset_y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, fillet_radius)

part = base
part.name = "XMountSocket"
export_step(part, "output.step")