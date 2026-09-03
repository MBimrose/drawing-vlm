from build123d import *

outer_width = 80.0
outer_height = 50.0
thickness = 5.0
wall_thickness = 3.0
fillet_radius = 0.5
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_y = 15.0
rib_width = 2.0
rib_height = 2.0
rib_spacing = 20.0

solid_body = Box(outer_width, outer_height, thickness)

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness
cavity_depth = thickness - 1.0
cavity = Box(inner_width, inner_height, cavity_depth)
solid_body = solid_body - Pos(0, 0, -thickness/2 + cavity_depth/2) * cavity

for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y),
             (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness)

num_ribs = int((outer_width - 2 * wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_pos = -outer_width / 2 + wall_thickness + rib_spacing / 2 + i * rib_spacing
    rib = Box(rib_width, outer_height - 2 * wall_thickness, rib_height)
    solid_body = solid_body + Pos(x_pos, 0, 0) * rib

front_face = solid_body.faces().sort_by(Axis.Z)[-1]
front_edges = front_face.edges()
solid_body = fillet(front_edges, fillet_radius)

part = solid_body
part.name = "plate_with_cavity_holes_and_ribs"
export_step(part, "output.step")