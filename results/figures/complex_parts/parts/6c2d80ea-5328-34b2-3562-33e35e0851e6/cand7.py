from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 70.0
leg_thickness = 10.0
bracket_thickness = 8.0
rib_height = 4.0
rib_width = 12.0
hole_diameter = 4.0
hole_depth = 4.0
hole_spacing = 15.0
hole_offset_from_corner = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_leg_length))
            l2 = Line(l1 @ 1, (leg_thickness, vertical_leg_length))
            l3 = Line(l2 @ 1, (leg_thickness, leg_thickness))
            l4 = Line(l3 @ 1, (horizontal_leg_length, leg_thickness))
            l5 = Line(l4 @ 1, (horizontal_leg_length, 0))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch(Plane.XY.offset(bracket_thickness)) as rib_sk:
        with BuildLine() as rib_bl:
            rl1 = Line((leg_thickness, leg_thickness), (leg_thickness + rib_width, leg_thickness))
            rl2 = Line(rl1 @ 1, (leg_thickness, leg_thickness + rib_width))
            rl3 = Line(rl2 @ 1, (leg_thickness, leg_thickness))
        make_face()
    extrude(amount=rib_height)

solid_body = solid_body + rib_p.part

for i in range(3):
    hx = hole_offset_from_corner + i * hole_spacing
    hy = leg_thickness / 2
    hz = bracket_thickness - hole_depth / 2
    solid_body = solid_body - Pos(hx, hy, hz) * Cylinder(hole_diameter / 2, hole_depth)

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")