from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
pulley_width = 20.0
tab_width = 20.0
tab_height = 12.0
keyway_width = 6.0
keyway_depth = 4.0
mount_hole_diameter = 8.0
mount_hole_spacing = 30.0
chamfer_distance = 0.5

result = Cylinder(outer_diameter / 2, pulley_width)
result = result + Pos(0, outer_diameter / 2, 0) * Box(tab_width, tab_height, pulley_width)
result = result - Cylinder(inner_diameter / 2, pulley_width)
result = result - Pos(0, 0, pulley_width - keyway_depth / 2) * Box(keyway_width, pulley_width, keyway_depth)
for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, pulley_width)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "pulley"
export_step(part, "output.step")