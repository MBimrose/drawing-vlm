from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 70.0
leg_width = 20.0
thickness = 10.0
slot_width = 4.0
slot_length = 20.0
hole_diameter = 5.0
hole_depth = thickness - 2.0
hole_spacing = 12.0
hole_offset_from_corner = 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_width),
                     (thickness, leg_width), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_center_x = thickness / 2
slot_center_y = vertical_leg_length / 2
slot_cut = Pos(slot_center_x, slot_center_y, thickness / 2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot_cut

hole_start_x = hole_offset_from_corner
hole_y = leg_width / 2
for i in range(4):
    hx = hole_start_x + i * hole_spacing
    hole_cut = Pos(hx, hole_y, thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - hole_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")