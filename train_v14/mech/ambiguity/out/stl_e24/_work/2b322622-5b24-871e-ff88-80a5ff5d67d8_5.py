from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
vent_hole_diameter = 4.0
vent_rows = 2
vent_cols = 4
vent_spacing_x = 15.0
vent_spacing_y = 20.0
diagonal_hole_diameter = 5.0
diagonal_hole_count = 6
diagonal_margin = 10.0
counterbore_diameter = 6.0
counterbore_depth = 2.5
rib_width = 10.0
rib_height = 3.0
rib_thickness = 2.0

solid = Box(plate_length, plate_width, plate_thickness)
solid = solid + Pos(0, 0, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

vent_start_x = -((vent_cols - 1) * vent_spacing_x) / 2
vent_start_y = -((vent_rows - 1) * vent_spacing_y) / 2
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_start_x + i * vent_spacing_x
        y = vent_start_y + j * vent_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, plate_thickness + 1)

diag_step_x = (plate_length - 2 * diagonal_margin) / (diagonal_hole_count - 1)
diag_step_y = (plate_width - 2 * diagonal_margin) / (diagonal_hole_count - 1)
for k in range(diagonal_hole_count):
    x = -plate_length/2 + diagonal_margin + k * diag_step_x
    y = -plate_width/2 + diagonal_margin + k * diag_step_y
    solid = solid - Pos(x, y, 0) * Cylinder(diagonal_hole_diameter/2, plate_thickness + 1)
    solid = solid - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid
part.name = "vent_plate_with_rib"
export_step(part, "output.step")