from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 6.0
frame_height = 8.0
frame_wall_thickness = 5.0
rib_height = 4.0
rib_width = 6.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = (base_length - 2 * frame_wall_thickness) / (hole_cols + 1)
hole_spacing_y = (base_width - 2 * frame_wall_thickness) / (hole_rows + 1)
fillet_radius = 0.5

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)
frame_outer = Pos(0, 0, base_thickness + frame_height / 2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height / 2) * Box(base_length - 2 * frame_wall_thickness, base_width - 2 * frame_wall_thickness, frame_height)
frame = frame_outer - frame_inner
rib = Pos(0, 0, base_thickness + rib_height / 2) * Box(base_length - 2 * frame_wall_thickness, rib_width, rib_height)

solid_body = base + frame + rib

hole_radius = hole_diameter / 2
hole_height = base_thickness + frame_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, base_thickness + frame_height / 2) * Cylinder(hole_radius, hole_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
inner_edges = [e for e in vertical_edges if abs(e.center().X) < 40 and abs(e.center().Y) < 30]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")