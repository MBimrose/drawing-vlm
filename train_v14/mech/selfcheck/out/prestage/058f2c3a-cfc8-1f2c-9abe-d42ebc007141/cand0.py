from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
gusset_height = 30.0
gusset_thickness = 4.0
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_margin = 6.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as g:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-gusset_height/2, plate_thickness/2), (gusset_height/2, plate_thickness/2))
            l2 = Line(l1@1, (0, plate_thickness/2 + gusset_thickness))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-gusset_thickness)

solid_body = solid_body + g.part

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
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

part = solid_body
part.name = "plate_with_gusset_and_holes"
export_step(part, "output.step")