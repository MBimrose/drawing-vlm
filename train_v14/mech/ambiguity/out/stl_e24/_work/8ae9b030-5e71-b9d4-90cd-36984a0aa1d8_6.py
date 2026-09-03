from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
thickness = 8.0
bracket_depth = 10.0
slot_width = 6.0
slot_length = 30.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_corner = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

slot = Pos(thickness/2, vertical_leg_length/2, bracket_depth/2) * Box(thickness, slot_length, slot_width)
solid_body = solid_body - slot

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    hole = Pos(x, thickness/2, bracket_depth/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")