from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 8.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 3.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
chamfer_distance = 0.5
central_hole_diameter = 6.0

base = Box(cover_length, cover_width, cover_thickness)
top_face = base.faces().sort_by(Axis.Z)[-1]
hollow = offset(base, amount=-wall_thickness, openings=[top_face])

rib1 = Pos(0, 0, wall_thickness) * Box(cover_length - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, wall_thickness) * Box(rib_thickness, cover_width - 2*wall_thickness, rib_height)
with_ribs = hollow + rib1 + rib2

central_hole = Cylinder(central_hole_diameter/2, cover_thickness + 2)
with_central = with_ribs - central_hole

points = []
start_x = -((hole_cols - 1) * hole_spacing_x) / 2.0
start_y = -((hole_rows - 1) * hole_spacing_y) / 2.0
for i in range(hole_cols):
    for j in range(hole_rows):
        points.append((start_x + i * hole_spacing_x, start_y + j * hole_spacing_y))

with_holes = with_central
for x, y in points:
    with_holes = with_holes - Pos(x, y, 0) * Cylinder(hole_diameter/2, cover_thickness + 2)

vertical_edges = with_holes.edges().filter_by(Axis.Z)
outer_edges = [e for e in vertical_edges if abs(e.center().X) > cover_length/2 - 1 or abs(e.center().Y) > cover_width/2 - 1]
result = chamfer(outer_edges, chamfer_distance)

part = result
part.name = "cover_plate"
export_step(part, "output.step")