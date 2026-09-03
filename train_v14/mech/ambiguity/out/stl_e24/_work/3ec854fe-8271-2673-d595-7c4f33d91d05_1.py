from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
rib_width = 10.0
rib_height = 4.0
rib_offset = 5.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2
chamfer_size = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Box(plate_length - 2 * rib_offset, rib_width, rib_height)
rib2 = Box(rib_width, plate_width - 2 * rib_offset, rib_height)

solid_body = base + rib1 + rib2

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2 - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")