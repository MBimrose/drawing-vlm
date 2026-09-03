from build123d import *
import math

block_length = 80.0
block_width = 60.0
block_thickness = 12.0
pocket_margin = 5.0
pocket_depth = 4.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
fillet_radius = 1.0
chamfer_distance = 1.0
rib_width = 20.0
rib_height = 2.0
rib_length = block_length - 2 * pocket_margin
boss_diameter = 15.0
boss_height = 2.0

result = Box(block_length, block_width, block_thickness)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

pocket_w = block_length - 2 * pocket_margin
pocket_h = block_width - 2 * pocket_margin
pocket = Pos(0, 0, block_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness + 1)

cs_depth = (countersink_diameter/2 - hole_diameter/2) / math.tan(math.radians(countersink_angle/2))
cs_cone = Pos(0, 0, block_thickness/2 - cs_depth/2) * Cone(hole_diameter/2, countersink_diameter/2, cs_depth)
result = result - cs_cone

rib = Pos(0, 0, block_thickness/2 - rib_height/2) * Box(rib_width, rib_length, rib_height)
result = result + rib

boss = Pos(0, 0, block_thickness/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

part = result
part.name = "block_with_pocket_holes_rib_boss"
export_step(part, "output.step")