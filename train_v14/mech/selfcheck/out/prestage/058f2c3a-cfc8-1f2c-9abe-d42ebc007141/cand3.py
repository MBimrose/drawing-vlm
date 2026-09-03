from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 4.0
rib_base = 30.0
hole_diameter = 3.0
hole_margin = 6.0
hole_cols = 4
hole_rows = 2
chamfer_size = 0.4

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
base = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base/2, plate_thickness/2), (rib_base/2, plate_thickness/2), (0, plate_thickness/2 + rib_height), close=True)
        make_face()
    extrude(amount=-rib_height)
rib = rib_p.part

solid_body = base + rib

x_spacing = (plate_length - 2 * hole_margin) / (hole_cols - 1)
y_spacing = (plate_width - 2 * hole_margin) / (hole_rows - 1)
for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_margin + i * x_spacing
        y = -plate_width/2 + hole_margin + j * y_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")