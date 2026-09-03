from build123d import *

outer_width = 80.0
outer_height = 50.0
plate_thickness = 5.0
wall_thickness = 3.0
cavity_depth = 3.0
rib_width = 2.0
rib_height = 2.0
rib_spacing = 20.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 0.2

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

result = Box(outer_width, outer_height, plate_thickness)

cavity = Pos(0, 0, -plate_thickness/2 + cavity_depth/2) * Box(inner_width, inner_height, cavity_depth)
result = result - cavity

num_ribs = int((outer_width - 2 * wall_thickness) // rib_spacing) + 1
rib_positions = [-(outer_width/2 - wall_thickness) + i * rib_spacing for i in range(num_ribs)]
for x in rib_positions:
    rib = Pos(x, 0, 0) * Box(rib_width, inner_height, rib_height)
    result = result + rib

hole_positions = [
    (-outer_width/2 + mount_hole_offset, -outer_height/2 + mount_hole_offset),
    ( outer_width/2 - mount_hole_offset, -outer_height/2 + mount_hole_offset),
    (-outer_width/2 + mount_hole_offset,  outer_height/2 - mount_hole_offset),
    ( outer_width/2 - mount_hole_offset,  outer_height/2 - mount_hole_offset),
]
for hx, hy in hole_positions:
    hole = Pos(hx, hy, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
    result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_cavity_ribs_and_holes"
export_step(part, "output.step")