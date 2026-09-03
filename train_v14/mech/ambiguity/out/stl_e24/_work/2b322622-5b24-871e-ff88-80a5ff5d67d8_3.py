from build123d import *

panel_length = 100.0
panel_width = 80.0
panel_thickness = 5.0
rib_height = 3.0
rib_width = 10.0
vent_hole_diameter = 4.0
vent_rows = 2
vent_columns = 4
vent_spacing_x = 15.0
vent_spacing_y = 20.0
vent_offset_x = 30.0
vent_offset_y = 30.0
counterbore_hole_diameter = 5.0
counterbore_diameter = 6.0
counterbore_depth = 2.5
counterbore_spacing = 12.0
counterbore_count = 6
counterbore_start_x = -panel_length/2 + 5.0
counterbore_start_y = -panel_width/2 + 5.0
chamfer_size = 0.5

solid = Box(panel_length, panel_width, panel_thickness)
solid = solid + Pos(0, panel_width/2 - rib_width/2, 0) * Box(panel_length, rib_width, rib_height)
solid = solid + Pos(0, -panel_width/2 + rib_width/2, 0) * Box(panel_length, rib_width, rib_height)

for i in range(vent_columns):
    for j in range(vent_rows):
        x = vent_offset_x + (i - (vent_columns-1)/2) * vent_spacing_x
        y = vent_offset_y + (j - (vent_rows-1)/2) * vent_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, panel_thickness + 10)

for k in range(counterbore_count):
    x = counterbore_start_x + k * counterbore_spacing
    y = counterbore_start_y + k * counterbore_spacing
    solid = solid - Pos(x, y, 0) * Cylinder(counterbore_hole_diameter/2, panel_thickness + 10)
    solid = solid - Pos(x, y, panel_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "panel_with_ribs_and_holes"
export_step(part, "output.step")