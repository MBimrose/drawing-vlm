from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 4.0
rib_base = 30.0
rib_thickness = 4.0
hole_diameter = 3.0
hole_edge_margin = 6.0
hole_rows = 2
hole_columns = 4
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-rib_base/2, plate_thickness/2), (rib_base/2, plate_thickness/2))
            l2 = Line(l1@1, (0, plate_thickness/2 + rib_height))
            l3 = Line(l2@1, (-rib_base/2, plate_thickness/2))
        make_face()
    extrude(amount=-rib_thickness)
rib = rib_p.part
rib = chamfer(rib.edges().filter_by(Axis.Z), chamfer_distance)

combined = base + rib

x_start = -plate_length/2 + hole_edge_margin
x_end = plate_length/2 - hole_edge_margin
x_spacing = (x_end - x_start) / (hole_columns - 1) if hole_columns > 1 else 0
y_start = -plate_width/2 + hole_edge_margin
y_end = plate_width/2 - hole_edge_margin
y_spacing = (y_end - y_start) / (hole_rows - 1) if hole_rows > 1 else 0

points = []
for i in range(hole_columns):
    x = x_start + i * x_spacing
    for j in range(hole_rows):
        y = y_start + j * y_spacing
        points.append((x, y))

for x, y in points:
    combined = combined - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

part = combined
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")