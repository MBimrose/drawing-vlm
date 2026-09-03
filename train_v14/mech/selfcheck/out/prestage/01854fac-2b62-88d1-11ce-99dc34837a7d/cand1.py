from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
cutout_corner_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
edge_chamfer = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_length)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as cutout_p:
    with BuildSketch() as cs:
        RectangleRounded(cutout_width, cutout_height, cutout_corner_radius)
    extrude(amount=plate_thickness)

solid_body = solid_body - cutout_p.part

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

part = solid_body
part.name = "plate_with_cutout_and_holes"
export_step(part, "output.step")