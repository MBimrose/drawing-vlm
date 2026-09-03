from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 5.0
rim_width = 4.0
rim_height = 6.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing = 18.0
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_length, plate_thickness)
rim_outer = Pos(0, 0, plate_thickness + rim_height / 2) * Box(plate_width, plate_length, rim_height)
rim_inner = Pos(0, 0, plate_thickness + rim_height / 2) * Box(plate_width - 2 * rim_width, plate_length - 2 * rim_width, rim_height)
rim = rim_outer - rim_inner
result = base + rim

for i in range(3):
    for j in range(3):
        x = (i - 1) * hole_spacing
        y = (j - 1) * hole_spacing
        hole = Pos(x, y, plate_thickness + rim_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
        result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rim_and_holes"
export_step(part, "output.step")