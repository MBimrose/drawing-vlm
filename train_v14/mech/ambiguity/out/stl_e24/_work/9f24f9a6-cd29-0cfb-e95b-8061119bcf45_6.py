from build123d import *
import math

base_length = 80.0
base_width = 20.0
base_thickness = 5.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
boss_diameter = 20.0
boss_height = 15.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_angle = 90.0
slot_width = 10.0
slot_depth = 3.0
chamfer_size = 0.5

result = Box(base_length, base_width, base_thickness)

mount_hole_x = -base_length/2 + mount_hole_offset
result = result - Pos(mount_hole_x, 0, 0) * Cylinder(mount_hole_diameter/2, base_thickness * 2)

boss = Pos(0, 0, base_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

csk_depth = (set_screw_head_diameter/2) / math.tan(math.radians(set_screw_head_angle/2))
csk_cone = Pos(0, 0, base_thickness/2 + boss_height - csk_depth/2) * Cone(set_screw_diameter/2, set_screw_head_diameter/2, csk_depth)
shaft_cyl = Pos(0, 0, base_thickness/2 + boss_height - csk_depth - (boss_height + base_thickness)/2) * Cylinder(set_screw_diameter/2, boss_height + base_thickness)
result = result - csk_cone - shaft_cyl

slot = Pos(base_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, base_thickness)
result = result - slot

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")