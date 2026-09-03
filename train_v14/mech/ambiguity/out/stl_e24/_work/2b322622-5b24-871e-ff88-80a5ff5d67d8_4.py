from build123d import *
import math

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
edge_chamfer = 0.5
rib_width = 6.0
rib_height = 2.0
rib_spacing = 20.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 15.0
hole_spacing_y = 20.0
diagonal_hole_diameter = 5.0
diagonal_hole_count = 6
diagonal_hole_offset = 5.0
counterbore_diameter = 6.0
counterbore_depth = 2.5

solid_body = Box(plate_length, plate_width, plate_thickness)

num_ribs_x = int((plate_length - rib_spacing) // rib_spacing) + 1
num_ribs_y = int((plate_width - rib_spacing) // rib_spacing) + 1
for i in range(num_ribs_x):
    for j in range(num_ribs_y):
        x = -plate_length/2 + rib_spacing/2 + i * rib_spacing
        y = -plate_width/2 + rib_spacing/2 + j * rib_spacing
        solid_body = solid_body + Pos(x, y, 0) * Box(rib_width, rib_width, rib_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

diag_len = math.hypot(plate_length - 2*diagonal_hole_offset, plate_width - 2*diagonal_hole_offset)
step = diag_len / (diagonal_hole_count - 1)
for i in range(diagonal_hole_count):
    t = i / (diagonal_hole_count - 1)
    x = -plate_length/2 + diagonal_hole_offset + t * (plate_length - 2*diagonal_hole_offset)
    y = -plate_width/2 + diagonal_hole_offset + t * (plate_width - 2*diagonal_hole_offset)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(diagonal_hole_diameter/2, plate_thickness + 10)
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

part = solid_body
part.name = "ribbed_plate_with_holes"
export_step(part, "output.step")