from build123d import *

arm_length = 30.0
arm_width = 20.0
thickness = 12.0
central_hole_diameter = 20.0
arm_hole_diameter = 6.0
arm_hole_offset = 14.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(arm_width, arm_width + 2 * arm_length)
        Rectangle(arm_width + 2 * arm_length, arm_width)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness * 2)

for x, y in [(arm_hole_offset, 0), (-arm_hole_offset, 0), (0, arm_hole_offset), (0, -arm_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(arm_hole_diameter / 2, thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "cross_plate"
export_step(part, "output.step")