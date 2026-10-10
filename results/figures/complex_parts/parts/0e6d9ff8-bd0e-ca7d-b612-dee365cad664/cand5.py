from build123d import *

leg_length = 60.0
leg_width = 20.0
thickness = 10.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_offset = 10.0
hole_diameter = 4.0
hole_offset = 10.0
chamfer_size = 0.5
rib_thickness = 2.0
rib_height = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

pocket_center_x = pocket_offset + pocket_width / 2
pocket_center_y = pocket_offset + pocket_width / 2
pocket = Pos(pocket_center_x, pocket_center_y, thickness - pocket_depth / 2) * Box(pocket_width, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_center_y = hole_offset
hole_center_z = thickness / 2
hole = Pos(leg_length / 2, hole_center_y, hole_center_z) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, leg_length + 10)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(leg_width / 2, leg_length + rib_thickness / 2, thickness / 2) * Box(rib_height, rib_thickness, leg_width)
solid_body = solid_body + rib1

rib2 = Pos(leg_length + rib_thickness / 2, leg_width / 2, thickness / 2) * Box(rib_thickness, rib_height, leg_width)
solid_body = solid_body + rib2

part = solid_body
part.name = "L_bracket_with_pocket_hole_and_ribs"
export_step(part, "output.step")