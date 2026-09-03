from build123d import *

panel_width = 100.0
panel_height = 80.0
panel_thickness = 5.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 6
connector_hole_diameter = 4.0
connector_rows = 2
connector_cols = 4
connector_spacing_x = 15.0
connector_spacing_y = 20.0
rib_thickness = 2.0
rib_height = panel_thickness

base = Box(panel_width, panel_height, panel_thickness)
rib_left = Pos(-panel_width/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, panel_height, rib_height)
rib_right = Pos(panel_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, panel_height, rib_height)
result = base + rib_left + rib_right

start_x = -panel_width/2 + hole_spacing/2
start_y = -panel_height/2 + hole_spacing/2
for i in range(hole_count):
    x = start_x + i * hole_spacing
    y = start_y + i * hole_spacing
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)
    result = result - Pos(x, y, panel_thickness/4) * Cylinder(hole_diameter*1.2/2, panel_thickness/2)

grid_origin_x = 0
grid_origin_y = 0
for row in range(connector_rows):
    for col in range(connector_cols):
        x = grid_origin_x + (col - (connector_cols-1)/2) * connector_spacing_x
        y = grid_origin_y + (row - (connector_rows-1)/2) * connector_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(connector_hole_diameter/2, panel_thickness * 2)

part = result
part.name = "panel_with_ribs_and_holes"
export_step(part, "output.step")