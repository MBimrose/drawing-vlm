from build123d import *

base_length = 80.0
base_width = 50.0
base_height = 15.0
wall_thickness = 2.0
boss_length = 30.0
boss_width = 20.0
boss_height = 10.0
slot_length = 60.0
slot_width = 8.0
slot_depth = 5.0
fillet_radius = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 2.5
mount_hole_offset = 12.0
cable_hole_diameter = 6.0
cable_hole_offset = 10.0

base = Pos(0, 0, base_height/2) * Box(base_length, base_width, base_height)
boss = Pos(0, 0, boss_height/2) * Box(boss_length, boss_width, boss_height)
result = base + boss

slot = Pos(0, -base_width/2 + slot_depth/2, base_height/2) * Box(slot_length, slot_depth, slot_width)
result = result - slot

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

top_face = result.faces().sort_by(Axis.Y)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

bottom_face = result.faces().sort_by(Axis.Y)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

cable_hole = Pos(base_length/2 - wall_thickness/2, -base_width/2 + cable_hole_offset, base_height/2) * Rot(0, 90, 0) * Cylinder(cable_hole_diameter/2, wall_thickness)
result = result - cable_hole

for x, y in [(-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset),
             (-mount_hole_offset, mount_hole_offset), (mount_hole_offset, mount_hole_offset)]:
    result = result - Pos(x, y, base_height/2) * Cylinder(mount_hole_diameter/2, base_height + 10)

part = result
part.name = "enclosure_with_boss_and_holes"
export_step(part, "output.step")