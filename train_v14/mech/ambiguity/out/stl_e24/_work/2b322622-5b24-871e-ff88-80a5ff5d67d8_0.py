from build123d import *

panel_width = 100.0
panel_height = 80.0
panel_thickness = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 20.0
grid_rows = 2
grid_cols = 4
connector_hole_diameter = 5.0
connector_spacing = 12.0
connector_count = 6
connector_offset_x = -panel_width/2 + 5.0
rib_width = 10.0
rib_height = 30.0
rib_thickness = 2.0
chamfer_size = 0.5

solid_body = Box(panel_width, panel_height, panel_thickness)

for row in range(grid_rows):
    for col in range(grid_cols):
        x = (col - (grid_cols - 1) / 2) * hole_spacing_x
        y = (row - (grid_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness)

for i in range(connector_count):
    x = connector_offset_x
    y = -panel_height/2 + 5 + i * connector_spacing
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(connector_hole_diameter/2, panel_thickness)
    solid_body = solid_body - Pos(x, y, panel_thickness/4) * Cylinder((connector_hole_diameter+1)/2, panel_thickness/2)

rib = Pos(-panel_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "panel_with_holes_and_rib"
export_step(part, "output.step")