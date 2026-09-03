from build123d import *
import math

bracket_length = 70.0
bracket_width = 40.0
bracket_thickness = 8.0
boss_diameter = 20.0
boss_height = 12.0
boss_offset_x = 15.0
boss_offset_y = 0.0
blind_hole_diameter = 8.0
blind_hole_depth = 6.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_length = 8.0
rib_height = 4.0
rib_offset_x = 0.0
rib_offset_y = -10.0
csk_angle = 82.0
csk_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

boss_x = boss_offset_x - bracket_length / 2
boss_y = boss_offset_y
solid_body = solid_body + Pos(boss_x, boss_y, bracket_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

csk_r = blind_hole_diameter / 2 + csk_depth * math.tan(math.radians(csk_angle / 2))
csk_hole = CounterSinkHole(blind_hole_diameter / 2, csk_r, csk_depth, csk_angle)
solid_body = solid_body - Pos(boss_x, boss_y, bracket_thickness + boss_height - csk_depth / 2) * csk_hole

blind_hole = Cylinder(blind_hole_diameter / 2, blind_hole_depth)
solid_body = solid_body - Pos(boss_x, boss_y, bracket_thickness + boss_height - blind_hole_depth / 2) * blind_hole

for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, bracket_thickness / 2) * Cylinder(mount_hole_diameter / 2, bracket_thickness + 1)

rib_x = rib_offset_x
rib_y = rib_offset_y
solid_body = solid_body + Pos(rib_x, rib_y, -rib_height / 2) * Box(rib_width, rib_length, rib_height)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")