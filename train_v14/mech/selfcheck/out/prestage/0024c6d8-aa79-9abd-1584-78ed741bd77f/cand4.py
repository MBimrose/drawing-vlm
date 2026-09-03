from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 70.0
leg_thickness = 10.0
leg_width = 20.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part

slot_center_x = leg_thickness / 2
slot_center_y = vertical_leg_length / 2
solid_body = solid_body - Pos(slot_center_x, slot_center_y, leg_thickness/2) * Box(slot_width, slot_length, leg_thickness)

hole_start_x = horizontal_leg_length - hole_offset_from_end - (hole_spacing * (4 - 1))
hole_y = leg_width / 2
for i in range(4):
    hx = hole_start_x + i * hole_spacing
    solid_body = solid_body - Pos(hx, hole_y, leg_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")