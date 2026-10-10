from build123d import *
import math

leg_length = 80.0
leg_width = 20.0
wall_thickness = 2.0
flange_thickness = 20.0
flange_radius = 30.0
hole_diameter = 5.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_width, 0))
            l2 = Line(l1 @ 1, (leg_width, leg_length - flange_thickness))
            l3 = Line(l2 @ 1, (leg_width + flange_radius, leg_length - flange_thickness))
            l4 = Line(l3 @ 1, (leg_width + flange_radius, leg_length))
            l5 = Line(l4 @ 1, (0, leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

for x, y in [(hole_offset, 0), (-hole_offset, 0), (0, hole_offset), (0, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, leg_length) * Cylinder(hole_diameter / 2, flange_thickness)

part = solid_body
part.name = "revolved_flange_with_holes"
export_step(part, "output.step")