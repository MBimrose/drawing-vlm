from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
through_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 70.0
mount_hole_offset = 5.0

result = Box(block_length, block_width, block_height)
result = result + Pos(0, 0, block_height/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Cylinder(through_hole_diameter/2, block_height + 20)
result = result - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, mount_hole_offset) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 20)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)
bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_distance)

part = result
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")