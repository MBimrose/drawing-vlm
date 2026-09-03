from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 12.0
hole_offset_x = 20.0
hole_offset_y = 15.0
fillet_radius = 4.0
chamfer_distance = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
pocket_depth = 10.0
pocket_width = 30.0
pocket_height = 20.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
boss = Pos(0, 0, block_height - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

hole_x = hole_offset_x - block_length/2
hole_y = hole_offset_y - block_width/2
result = result - Pos(hole_x, hole_y, block_height/2) * Cylinder(hole_diameter/2, block_height + 20)

for i in range(2):
    for j in range(2):
        mx = (i - 0.5) * mount_hole_spacing
        my = (j - 0.5) * mount_hole_spacing
        result = result - Pos(mx, my, block_height/2) * Cylinder(mount_hole_diameter/2, block_height + 20)

pocket = Pos(0, -block_width/2 + pocket_depth/2, block_height/2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

right_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-4:]
result = fillet(right_edges, fillet_radius)

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")