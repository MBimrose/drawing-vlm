from build123d import *

arm_length = 70.0
boss_diameter = 20.0
boss_height = 10.0
tip_diameter = 5.0
fillet_radius = 2.0
slot_width = 8.0
slot_depth = 4.0
slot_offset = 30.0
mount_hole_dia = 4.0
mount_hole_spacing = 15.0
rib_thickness = 2.0
rib_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(boss_diameter / 2)
    with BuildSketch(Plane.XY.offset(boss_height)) as s2:
        Circle(boss_diameter / 2)
    with BuildSketch(Plane.XY.offset(arm_length)) as s3:
        Circle(tip_diameter / 2)
    loft()

arm_body = p.part
boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
result = arm_body + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

slot_box = Pos(0, slot_offset, arm_length - slot_depth / 2) * Box(slot_width, slot_depth, slot_depth)
result = result - slot_box

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    result = result - Pos(x, 0, arm_length / 2) * Cylinder(mount_hole_dia / 2, arm_length + 10)

result = result - Pos(0, 0, boss_height / 2) * Cylinder(mount_hole_dia / 2, boss_height + 10)

rib = Pos(boss_diameter / 2 - rib_thickness / 2, 0, arm_length / 2) * Box(rib_thickness, rib_height, arm_length)
result = result + rib

part = result
part.name = "arm_with_boss"
export_step(part, "output.step")