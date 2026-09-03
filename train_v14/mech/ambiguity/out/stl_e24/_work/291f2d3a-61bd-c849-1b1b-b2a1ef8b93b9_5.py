from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 8.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 2.0
vent_hole_diameter = 4.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 12.0
vent_spacing_y = 12.0
central_hole_diameter = 6.0
chamfer_size = 0.5

base = Box(cover_length, cover_width, cover_thickness)
top_face = base.faces().sort_by(Axis.Z)[-1]
shell_body = offset(base, amount=-wall_thickness, openings=[top_face])

rib1 = Pos(0, 0, rib_height/2) * Box(cover_length - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, rib_height/2) * Box(rib_thickness, cover_width - 2*wall_thickness, rib_height)
shell_body = shell_body + rib1 + rib2

shell_body = shell_body - Cylinder(central_hole_diameter/2, cover_thickness + 1)

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        shell_body = shell_body - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, cover_thickness + 1)

vertical_edges = shell_body.edges().filter_by(Axis.Z)
shell_body = chamfer(vertical_edges, chamfer_size)

part = shell_body
part.name = "ventilated_cover"
export_step(part, "output.step")