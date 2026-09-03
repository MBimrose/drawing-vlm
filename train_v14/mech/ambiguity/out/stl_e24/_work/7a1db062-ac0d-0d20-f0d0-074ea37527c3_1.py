from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
central_hole_diameter = 12.0
set_screw_diameter = 4.2
set_screw_offset = boss_diameter / 4.0
pocket_length = 30.0
pocket_width = 6.0
pocket_depth = 8.0
chamfer_size = 0.5
fillet_radius = 1.0

base = Box(block_length, block_width, block_thickness)
boss = Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

hole = Pos(0, 0, boss_height/2) * Cylinder(central_hole_diameter/2, block_thickness + boss_height + 2)
result = result - hole

set_screw = Pos(set_screw_offset, 0, boss_height/2) * Cylinder(set_screw_diameter/2, block_thickness + boss_height + 2)
result = result - set_screw

pocket = Pos(0, 0, block_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
bottom_edges = result.edges().sort_by(Axis.Z)[:1]
result = fillet(bottom_edges, fillet_radius)

part = result
part.name = "block_with_boss_and_pocket"
export_step(part, "output.step")