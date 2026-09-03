from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 12.0
boss_height = 20.0
boss_offset_x = 20.0
boss_offset_y = 15.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 10.0
fillet_radius = 4.0
chamfer_distance = 2.0
hole_diameter = 6.0
hole_spacing = 30.0

result = Box(block_length, block_width, block_height)

boss = Pos(boss_offset_x - block_length/2, boss_offset_y - block_width/2, 0) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

pocket = Pos(0, -block_width/2 + pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

for dx in [-hole_spacing/2, hole_spacing/2]:
    for dy in [-hole_spacing/2, hole_spacing/2]:
        hole = Pos(dx, dy, 0) * Cylinder(hole_diameter/2, block_height + 10)
        result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_distance)

right_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-3:]
result = fillet(right_edges, fillet_radius)

part = result
part.name = "block_with_boss_pocket_holes"
export_step(part, "output.step")