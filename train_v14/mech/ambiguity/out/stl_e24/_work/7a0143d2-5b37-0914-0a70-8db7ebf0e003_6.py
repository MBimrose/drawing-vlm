from build123d import *

vertical_leg = 70.0
horizontal_leg = 80.0
thickness = 10.0
slot_width = 5.0
slot_height = 10.0
slot_center_x = 40.0
slot_center_y = 35.0
hole_diameter = 5.0
hole_spacing = 40.0
hole_center_y = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg), (horizontal_leg, vertical_leg),
                     (horizontal_leg, vertical_leg - thickness),
                     (thickness, vertical_leg - thickness), (thickness, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_box = Box(slot_width, slot_height, thickness)
solid_body = solid_body - Pos(slot_center_x, vertical_leg - thickness/2, thickness/2) * slot_box

hole_cyl = Rot(90, 0, 0) * Cylinder(hole_diameter/2, thickness)
for x in [horizontal_leg/2 - hole_spacing/2, horizontal_leg/2 + hole_spacing/2]:
    solid_body = solid_body - Pos(x, vertical_leg - thickness/2, thickness/2) * hole_cyl

bottom_left_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[:1].sort_by(Axis.Y)[:1]
solid_body = chamfer(bottom_left_edge, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")