from build123d import *

cover_length = 80.0
cover_width = 50.0
cover_thickness = 5.0
wall_thickness = 3.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_offset = 10.0
rib_thickness = 2.0
rib_spacing = 20.0
rib_notch_width = 1.0
rib_notch_depth = 0.5

inner_length = cover_length - 2 * wall_thickness
inner_width = cover_width - 2 * wall_thickness
cavity_depth = cover_thickness - wall_thickness
pocket_depth = 1.0
pocket_length = inner_length - 2 * pocket_depth
pocket_width = inner_width - 2 * pocket_depth

result = Box(cover_length, cover_width, cover_thickness)
result = result - Pos(0, 0, cover_thickness/2 - cavity_depth/2) * Box(inner_length, inner_width, cavity_depth)
result = result - Pos(0, 0, cover_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

hole_positions = [
    (-cover_length/2 + hole_offset, -cover_width/2 + hole_offset),
    ( cover_length/2 - hole_offset, -cover_width/2 + hole_offset),
    (-cover_length/2 + hole_offset,  cover_width/2 - hole_offset),
    ( cover_length/2 - hole_offset,  cover_width/2 - hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, cover_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

num_ribs = int((cover_length - 2 * wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_pos = -cover_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, 0) * Box(rib_thickness, inner_width, rib_thickness)
    notch = Pos(x_pos, 0, rib_thickness/2 - rib_notch_depth/2) * Box(rib_notch_width, inner_width, rib_notch_depth)
    result = result + (rib - notch)

part = result
part.name = "cover_with_ribs"
export_step(part, "output.step")