from build123d import *

outer_diameter = 60.0
length = 30.0
wall_thickness = 8.0
keyway_width = 6.0
keyway_depth = wall_thickness - 2.0
chamfer_size = 1.0
rib_thickness = 2.0
rib_height = 5.0
rib_count = 4
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = wall_thickness - 1.0
inner_radius = outer_diameter / 2 - wall_thickness

result = Cylinder(outer_diameter / 2, length) - Cylinder(inner_radius, length)

keyway = Pos(inner_radius - keyway_depth / 2, 0, 0) * Box(keyway_width, length, length)
result = result - keyway

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter / 2 - rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_height, length)
    result = result + rib

pocket = Pos(0, outer_diameter / 2 - pocket_depth / 2, 0) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

part = result
part.name = "tube_with_keyway_ribs_pocket"
export_step(part, "output.step")