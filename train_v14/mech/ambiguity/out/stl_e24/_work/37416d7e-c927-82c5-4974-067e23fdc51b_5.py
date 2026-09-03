from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
boss_radius = 8.0
boss_height = 5.0
chamfer_distance = 3.0
hole_diameter = 5.0
hole_offset = 10.0
rib_thickness = 2.0
rib_width = 4.0
rib_height = 6.0
rib_spacing = 15.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(0, 0, arm_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

hole_positions = [
    (-arm_length/2 + hole_offset, -arm_width/2 + hole_offset),
    ( arm_length/2 - hole_offset, -arm_width/2 + hole_offset),
    (-arm_length/2 + hole_offset,  arm_width/2 - hole_offset),
    ( arm_length/2 - hole_offset,  arm_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, arm_thickness/2 + boss_height/2) * Cylinder(hole_diameter/2, arm_thickness + boss_height + 10)

rib_count = int((arm_length - 2*hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -arm_length/2 + hole_offset + i * rib_spacing
    rib = Pos(x_pos, 0, rib_height/2) * Box(rib_width, rib_thickness, rib_height)
    result = result + rib

part = result
part.name = "arm_with_boss_and_ribs"
export_step(part, "output.step")