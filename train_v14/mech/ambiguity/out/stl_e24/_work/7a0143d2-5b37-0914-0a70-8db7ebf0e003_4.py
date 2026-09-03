from build123d import *

vertical_leg_height = 70.0
horizontal_leg_length = 80.0
thickness = 10.0
slot_width = 5.0
slot_depth = 5.0
slot_offset = 5.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (thickness, 0), (thickness, vertical_leg_height - thickness),
                     (horizontal_leg_length, vertical_leg_height - thickness),
                     (horizontal_leg_length, vertical_leg_height), (0, vertical_leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_center_x = horizontal_leg_length / 2
slot_center_y = vertical_leg_height - slot_offset
slot_box = Pos(slot_center_x, slot_center_y, thickness / 2) * Box(slot_width, slot_depth, thickness)
solid_body = solid_body - slot_box

hole_center_x = horizontal_leg_length / 2
hole_center_z = thickness / 2
for dx in [-hole_spacing / 2, hole_spacing / 2]:
    hx = hole_center_x + dx
    hole = Pos(hx, vertical_leg_height, hole_center_z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, 200)
    solid_body = solid_body - hole

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1]
solid_body = chamfer(chamfer_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")