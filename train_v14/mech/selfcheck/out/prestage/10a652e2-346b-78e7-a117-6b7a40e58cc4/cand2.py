from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
leg_thickness = 10.0
extrude_depth = 20.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 5.0
hole_offset_y = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid = p.part
solid = fillet(solid.edges(), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = hole_offset_y + (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid = solid - Pos(x, y, extrude_depth / 2) * Cylinder(hole_diameter / 2, extrude_depth)

part = solid
part.name = "L_bracket_with_holes"
export_step(part, "output.step")