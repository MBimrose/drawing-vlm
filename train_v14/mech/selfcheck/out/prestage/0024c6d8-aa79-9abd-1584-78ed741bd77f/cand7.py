from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 70.0
leg_width = 20.0
thickness = 10.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_offset_from_end = 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (thickness, leg_width), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot = Pos(thickness/2, vertical_leg_length/2, thickness/2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot

for i in range(4):
    x = hole_offset_from_end + i * hole_spacing
    y = leg_width / 2
    hole = Pos(x, y, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")