from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 30.0
rib_thickness = 4.0
rib_extension = 8.0
hole_diameter = 3.0
hole_margin = 6.0
hole_rows = 2
hole_cols = 4
fillet_radius = 0.5

with BuildPart() as p:
    Box(plate_length, plate_width, plate_thickness)
base = p.part
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_height/2, -rib_thickness/2), (rib_height/2, -rib_thickness/2), (0, rib_thickness/2), close=True)
        make_face()
    extrude(amount=-rib_extension)
rib = rib_p.part

result = base + rib

x_start = -plate_length/2 + hole_margin
x_end = plate_length/2 - hole_margin
y_start = -plate_width/2 + hole_margin
y_end = plate_width/2 - hole_margin
x_spacing = (x_end - x_start) / (hole_cols - 1) if hole_cols > 1 else 0
y_spacing = (y_end - y_start) / (hole_rows - 1) if hole_rows > 1 else 0

for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * x_spacing
        y = y_start + j * y_spacing
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")