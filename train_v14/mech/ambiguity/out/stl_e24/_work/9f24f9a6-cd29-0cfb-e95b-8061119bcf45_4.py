from build123d import *
import math

base_length = 80.0
base_width = 20.0
base_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_angle = 90.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
slot_width = 4.0
slot_length = 15.0
chamfer_size = 0.5

base = Box(base_length, base_width, base_thickness)
boss = Pos(0, 0, base_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = base + boss

csk_depth = (set_screw_head_diameter / 2) / math.tan(math.radians(set_screw_head_angle / 2))
csk_cone = Pos(0, 0, base_thickness + boss_height - csk_depth) * Cone(0, set_screw_head_diameter / 2, csk_depth)
shaft_cyl = Cylinder(set_screw_diameter / 2, base_thickness + boss_height + 10)
result = result - csk_cone - shaft_cyl

for x in [-mount_hole_offset, 2 * mount_hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, base_thickness + 10)

slot = Pos(base_length / 2 - base_thickness / 2, 0, 0) * Box(base_thickness, slot_width, slot_length)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")