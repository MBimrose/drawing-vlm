from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
central_hole_diameter = 10.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset = 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,leg_width), (leg_width,leg_width), (leg_width,leg_length), (0,leg_length), close=True)
        make_face()
    extrude(amount=thickness)
base = p.part

boss = Pos(leg_width/2, leg_width/2, thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = result - Pos(leg_width/2, leg_width/2, (thickness + boss_height)/2) * Cylinder(central_hole_diameter/2, thickness + boss_height + 10)

for i in range(3):
    x = hole_offset + i * hole_spacing
    result = result - Pos(x, 0, thickness/2) * Cylinder(hole_diameter/2, thickness + 10)

for i in range(3):
    y = hole_offset + i * hole_spacing
    result = result - Pos(0, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "L_bracket_with_boss"
export_step(part, "output.step")