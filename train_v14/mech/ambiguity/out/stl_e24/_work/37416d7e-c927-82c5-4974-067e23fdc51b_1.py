from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
boss_radius = 8.0
boss_height = 5.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_distance = 2.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(0, 0, arm_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

hole_positions = [
    (-arm_length/2 + hole_offset, -arm_width/2 + hole_diameter/2 + 3),
    ( arm_length/2 - hole_offset, -arm_width/2 + hole_diameter/2 + 3),
    (-arm_length/2 + hole_offset,  arm_width/2 - hole_diameter/2 - 3),
    ( arm_length/2 - hole_offset,  arm_width/2 - hole_diameter/2 - 3),
]

for x, y in hole_positions:
    result = result - Pos(x, y, (arm_thickness + boss_height)/2) * Cylinder(hole_diameter/2, arm_thickness + boss_height + 10)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "arm_with_boss_and_holes"
export_step(part, "output.step")