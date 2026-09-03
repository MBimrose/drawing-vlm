from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
inlet_radius = 6.0
inlet_offset_z = 30.0
chamfer_size = 1.0

inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness

base = Box(outer_width, outer_depth, outer_height)
inner_cut = Box(inner_width, inner_depth, outer_height + 0.2)
result = base - inner_cut

hole = Pos(-outer_width/2 + wall_thickness/2, 0, inlet_offset_z - outer_height/2) * Rot(0, 90, 0) * Cylinder(inlet_radius, wall_thickness + 2)
result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "XMountSocket"
export_step(part, "output.step")