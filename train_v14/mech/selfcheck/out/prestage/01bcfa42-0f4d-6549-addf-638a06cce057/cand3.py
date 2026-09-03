from build123d import *

plate_length = 80
plate_width = 60
plate_thickness = 5
blind_hole_diameter = 6
blind_hole_depth = 2

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
hole = Pos(0, 0, plate_thickness - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_blind_hole"
export_step(part, "output.step")