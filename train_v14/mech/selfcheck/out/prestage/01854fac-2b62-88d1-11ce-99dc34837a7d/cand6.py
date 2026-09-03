from build123d import *

panel_width = 80.0
panel_height = 100.0
panel_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
cutout_fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
edge_chamfer = 1.0

solid_body = Box(panel_width, panel_height, panel_thickness)

cutout = Box(cutout_width, cutout_height, panel_thickness + 0.01)
cutout = fillet(cutout.edges().filter_by(Axis.Z), cutout_fillet_radius)
solid_body = solid_body - cutout

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, panel_thickness + 0.01)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

part = solid_body
part.name = "panel_with_cutout_and_holes"
export_step(part, "output.step")