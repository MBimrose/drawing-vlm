from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
central_hole_diameter = 10.0
through_hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body + Pos(leg_width/2, leg_width/2, thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(leg_width/2, leg_width/2, (thickness + boss_height)/2) * Cylinder(central_hole_diameter/2, thickness + boss_height + 2)

for i in range(4):
    x = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, thickness/2) * Cylinder(through_hole_diameter/2, thickness + 2)

for i in range(4):
    y = hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(0, y, thickness/2) * Cylinder(through_hole_diameter/2, thickness + 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "L_bracket_with_boss"
export_step(part, "output.step")