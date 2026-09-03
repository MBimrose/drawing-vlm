from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
rib_height = 3.0
rib_width = 6.0
rib_spacing = 12.0
hole_diameter = 5.0
hole_depth = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib = Box(rib_width, rib_width, rib_height)
rib_count_x = int((plate_length - rib_spacing) // (rib_width + rib_spacing))
rib_count_y = int((plate_width - rib_spacing) // (rib_width + rib_spacing))
rib_grid = Compound([Pos(i * (rib_width + rib_spacing), j * (rib_width + rib_spacing), 0) * rib for i in range(rib_count_x) for j in range(rib_count_y)])
plate_with_ribs = base + rib_grid

hole_cyl = Cylinder(hole_diameter / 2, hole_depth)
hole_positions = [((i - (hole_cols - 1) / 2) * hole_spacing_x, (j - (hole_rows - 1) / 2) * hole_spacing_y) for i in range(hole_cols) for j in range(hole_rows)]
plate_with_holes = plate_with_ribs - Compound([Pos(x, y, plate_thickness - hole_depth / 2) * hole_cyl for x, y in hole_positions])

part = chamfer(plate_with_holes.edges().filter_by(Axis.Z), chamfer_size)
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")