from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
boss_radius = 8.0
boss_height = 5.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_distance = 2.0
rib_width = 6.0
rib_height = 2.0
rib_offset = 20.0

base = Pos(0, 0, arm_thickness / 2) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(0, 0, arm_thickness + boss_height / 2) * Cylinder(boss_radius, boss_height)
rib1 = Pos(-rib_offset, 0, arm_thickness / 2) * Box(rib_width, rib_height, arm_thickness)
rib2 = Pos(rib_offset, 0, arm_thickness / 2) * Box(rib_width, rib_height, arm_thickness)

solid_body = base + boss + rib1 + rib2

hole_positions = [
    (-arm_length / 2 + hole_offset, arm_width / 2 - hole_diameter / 2),
    (-arm_length / 2 + hole_offset, -arm_width / 2 + hole_diameter / 2),
    (arm_length / 2 - hole_offset, arm_width / 2 - hole_diameter / 2),
    (arm_length / 2 - hole_offset, -arm_width / 2 + hole_diameter / 2),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness + boss_height + 10)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "arm_with_boss_and_ribs"
export_step(part, "output.step")