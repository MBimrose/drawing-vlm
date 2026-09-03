from build123d import *

outer_width = 80.0
outer_height = 60.0
outer_depth = 12.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 8.0
fillet_radius = 1.5
chamfer_distance = 1.0
hole_diameter = 3.0
hole_offset = 10.0

base = Pos(0, 0, outer_depth/2) * Box(outer_width, outer_height, outer_depth)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

boss = Pos(0, 0, outer_depth + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

hole_positions = [
    (-outer_width/2 + hole_offset, -outer_height/2 + hole_offset),
    ( outer_width/2 - hole_offset, -outer_height/2 + hole_offset),
    (-outer_width/2 + hole_offset,  outer_height/2 - hole_offset),
    ( outer_width/2 - hole_offset,  outer_height/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, outer_depth + boss_height/2) * Cylinder(hole_diameter/2, outer_depth + boss_height + 20)

part = result
part.name = "shelled_box_with_boss"
export_step(part, "output.step")