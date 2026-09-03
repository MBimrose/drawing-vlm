from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 12.0
chamfer_distance = 0.5
hole_diameter = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 5.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib_count = int((inner_width - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -inner_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(0, y_pos, wall_thickness + inner_height/2) * Box(inner_length, rib_thickness, rib_height)
    base = base + rib

hole_positions = [
    (-hole_spacing_x/2, -hole_spacing_y/2),
    (hole_spacing_x/2, -hole_spacing_y/2),
    (-hole_spacing_x/2, hole_spacing_y/2),
    (hole_spacing_x/2, hole_spacing_y/2),
]
for x, y in hole_positions:
    base = base - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

top_face = base.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
base = chamfer(top_edges, chamfer_distance)

part = base
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")