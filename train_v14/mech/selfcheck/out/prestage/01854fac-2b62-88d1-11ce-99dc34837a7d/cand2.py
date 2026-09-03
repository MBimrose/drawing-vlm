from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
cutout_width = 40.0
cutout_length = 30.0
rib_width = 30.0
rib_length = 30.0
rib_height = 5.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

base = Box(plate_width, plate_length, plate_thickness)
cutout = Box(cutout_width, cutout_length, plate_thickness)
base = base - cutout

rib = Box(rib_width, rib_length, rib_height)
combined = base + rib

start_x = -((hole_cols - 1) * hole_spacing_x) / 2.0
start_y = -((hole_rows - 1) * hole_spacing_y) / 2.0
for i in range(hole_cols):
    for j in range(hole_rows):
        px = start_x + i * hole_spacing_x
        py = start_y + j * hole_spacing_y
        combined = combined - Pos(px, py, 0) * Cylinder(hole_diameter / 2, 100)

vertical_edges = combined.edges().filter_by(Axis.Z)
combined = chamfer(vertical_edges, chamfer_size)

part = combined
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")