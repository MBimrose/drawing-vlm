from build123d import *

leg_length = 80.0
leg_width = 70.0
leg_thickness = 15.0
base_thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
boss_hole_diameter = 10.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_width + leg_thickness),
                     (0, leg_width + leg_thickness), close=True)
        make_face()
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = solid_body + Pos(leg_thickness, leg_thickness, base_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(leg_thickness, leg_thickness, (base_thickness + boss_height)/2) * Cylinder(boss_hole_diameter/2, base_thickness + boss_height + 10)

for i in range(3):
    x = leg_thickness + hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 10)

for i in range(3):
    y = leg_thickness + hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(0, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 10)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")