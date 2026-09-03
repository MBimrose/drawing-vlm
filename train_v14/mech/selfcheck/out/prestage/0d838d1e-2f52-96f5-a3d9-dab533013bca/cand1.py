from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 4
chamfer_size = 1.0
rib_width = 10.0
rib_thickness = 4.0
rib_spacing = 30.0

base = Box(plate_length, plate_width, plate_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * pocket
pocket_edges = pocket.edges().filter_by(Axis.Z)
pocket = chamfer(pocket_edges, chamfer_size)

result = base - pocket

hole_radius = hole_diameter / 2
hole_height = plate_thickness + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_radius, hole_height)

rib_count = int((plate_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Box(rib_width, rib_thickness, rib_thickness)
    rib = Pos(x, 0, -plate_thickness/2 - rib_thickness/2) * rib
    result = result + rib

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")