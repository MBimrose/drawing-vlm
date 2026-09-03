from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_height = 2.0
rib_width = 10.0
rib_length = 30.0
recess_radius = 15.0
recess_depth = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness / 2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

recess = Pos(0, 0, plate_thickness - recess_depth / 2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - recess

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_rib_recess_and_holes"
export_step(part, "output.step")