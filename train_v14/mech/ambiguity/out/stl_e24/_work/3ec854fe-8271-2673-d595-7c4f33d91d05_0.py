from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
groove_width = 10.0
groove_depth = 2.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.8
rib_thickness = 4.0
rib_length = 20.0

result = Box(plate_length, plate_width, plate_thickness)

groove = Pos(0, 0, plate_thickness - groove_depth/2) * Box(plate_length - 2*groove_width, plate_width - 2*groove_width, groove_depth)
result = result - groove

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
        result = result - hole

rib_left = Pos(-plate_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_length, plate_thickness)
rib_right = Pos(plate_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_length, plate_thickness)
result = result + rib_left + rib_right

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_groove_holes_and_ribs"
export_step(part, "output.step")