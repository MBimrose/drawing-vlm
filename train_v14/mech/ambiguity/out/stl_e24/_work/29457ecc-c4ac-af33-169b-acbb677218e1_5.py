from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
hole_diameter = 5.0
hole_depth = 4.0
hole_rows = 3
hole_cols = 4
hole_spacing_x = 12.0
hole_spacing_y = 12.0
fillet_radius = 1.5
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(cover_length, cover_width)
    extrude(amount=cover_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

boss = Pos(0, 0, cover_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

x_start = -((hole_cols - 1) * hole_spacing_x) / 2
y_start = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * hole_spacing_x
        y = y_start + j * hole_spacing_y
        hole = Pos(x, y, cover_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
        solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "cover_with_boss_and_holes"
export_step(part, "output.step")