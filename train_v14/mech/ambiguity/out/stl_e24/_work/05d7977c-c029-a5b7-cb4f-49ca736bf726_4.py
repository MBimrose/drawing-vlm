from build123d import *

block_length = 60.0
block_width = 40.0
block_thickness = 8.0
boss_diameter = 20.0
boss_height = 4.0
hole_diameter = 6.0
hole_offset = 15.0
rib_width = 5.0
rib_length = 30.0
rib_height = 2.0
rib_spacing = 20.0
fillet_radius = 2.0
chamfer_distance = 0.5

result = Box(block_length, block_width, block_thickness)
result = result + Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness + boss_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    result = result + Pos(x, y, -block_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "block_with_boss_ribs"
export_step(part, "output.step")