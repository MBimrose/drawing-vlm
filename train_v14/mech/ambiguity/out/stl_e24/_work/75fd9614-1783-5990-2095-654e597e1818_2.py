from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
boss_diameter = 32.0
boss_height = 12.0
fillet_radius = 2.0
hole_diameter = 6.0
rib_thickness = 5.0
rib_width = 20.0
rib_height = 20.0
pocket_width = 6.0
pocket_height = 20.0
pocket_depth = 8.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
boss = Pos(-block_length/4, -block_width/4, block_height - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
rib = Pos(-block_length/2 + rib_thickness/2, 0, block_height/2) * Box(rib_thickness, rib_width, rib_height)
pocket = Pos(block_length/2 - pocket_depth/2, 0, block_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid = base + boss + rib - pocket

solid = solid - Pos(0, 0, block_height/2) * Cylinder(hole_diameter/2, block_height + 10)
for dx in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    for dy in [-mount_hole_spacing/2, mount_hole_spacing/2]:
        solid = solid - Pos(dx, dy, block_height/2) * Cylinder(mount_hole_diameter/2, block_height + 10)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "block_with_boss_rib_pocket"
export_step(part, "output.step")