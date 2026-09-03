from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
slot_width = 6.0
slot_height = 20.0
slot_depth = wall_thickness
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
fillet_radius = 2.0
boss_diameter = 20.0
boss_height = 4.0

result = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

slot = Pos(block_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
result = result - slot

result = result - Cylinder(through_hole_diameter/2, block_height)

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        result = result - Pos(dx, dy, 0) * Cylinder(mount_hole_diameter/2, block_height)

boss = Pos(-block_length/4, -block_width/4, block_height/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "block_with_pocket_slot_holes_boss"
export_step(part, "output.step")