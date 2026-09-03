from build123d import *

panel_width = 100.0
panel_height = 80.0
panel_thickness = 5.0
tab_width = 20.0
tab_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 4
connector_hole_diameter = 5.0
connector_hole_spacing = 12.0
connector_hole_count = 6
connector_start_y = -panel_height/2 + 10.0
chamfer_distance = 0.5
cbore_radius = 2.5
cbore_outer_radius = 3.0
cbore_depth = 2.5

solid_body = Box(panel_width, panel_height, panel_thickness) + Pos(panel_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, panel_thickness)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness)

for i in range(connector_hole_count):
    x = -panel_width/2 + 5.0
    y = connector_start_y + i * connector_hole_spacing
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(connector_hole_diameter/2, panel_thickness)
    solid_body = solid_body - Pos(x, y, panel_thickness/2 - cbore_depth/2) * Cylinder(cbore_outer_radius, cbore_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "panel_with_tabs_and_holes"
export_step(part, "output.step")