from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 15.0
outer_chamfer = 5.0
inner_diameter = 30.0
boss_diameter = 50.0
boss_height = 60.0
mount_hole_diameter = 8.0
mount_hole_offset = 25.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 10.0
edge_chamfer = 1.0
clearance = 0.5

base = Box(base_length, base_width, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), outer_chamfer)
base = base - Cylinder(inner_diameter/2, base_thickness)

boss = Pos(0, 0, base_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

hole_h = base_thickness + boss_height + 10
for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, hole_h)

pocket = Pos(0, 0, base_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

result = chamfer(result.edges(), edge_chamfer)

part = result
part.name = "base_with_boss_and_pocket"
export_step(part, "output.step")