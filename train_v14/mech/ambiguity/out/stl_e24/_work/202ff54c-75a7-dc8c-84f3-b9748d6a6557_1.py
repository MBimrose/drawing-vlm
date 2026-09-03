from build123d import *
import math

outer_diameter = 80
inner_diameter = 40
length = 60
wall_thickness = (outer_diameter - inner_diameter) / 2
keyway_width = 12
keyway_depth = wall_thickness * 0.6
keyway_length = length * 0.6
keyway_offset = (length - keyway_length) / 2
chamfer_size = 3
mount_hole_dia = 4
mount_hole_offset = 10
rib_height = length * 0.5
rib_width = 6
rib_thickness = wall_thickness * 0.8
rib_count = 4

result = Cylinder(outer_diameter / 2, length)
result = result - Cylinder(inner_diameter / 2, length)

keyway = Pos(outer_diameter / 2 - keyway_depth / 2, 0, keyway_offset) * Box(keyway_depth, keyway_width, keyway_length)
result = result - keyway

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for x, y in [(outer_diameter / 2 - mount_hole_offset, 0), (-(outer_diameter / 2 - mount_hole_offset), 0)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, length)

for i in range(rib_count):
    angle = i * 360 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter / 2, 0, 0) * Box(rib_thickness, rib_width, rib_height)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_keyway_and_ribs"
export_step(part, "output.step")