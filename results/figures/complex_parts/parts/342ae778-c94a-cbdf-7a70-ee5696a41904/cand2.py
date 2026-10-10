from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
block_height = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
mount_hole_offset = 15.0
rib_width = 6.0
rib_height = 8.0
rib_thickness = 5.0
rib_count = 12
slot_width = 10.0
slot_length = 30.0
slot_depth = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

result = Cylinder(outer_radius, block_height)
result = result - Cylinder(inner_radius, block_height)
result = result - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

mount_points = [
    (-mount_hole_spacing/2, -mount_hole_offset/2),
    (mount_hole_spacing/2, -mount_hole_offset/2),
    (-mount_hole_spacing/2, mount_hole_offset/2),
    (mount_hole_spacing/2, mount_hole_offset/2),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

result = result - Pos(-outer_radius + slot_depth/2, 0, block_height/4) * Box(slot_depth, slot_width, slot_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

part = result
part.name = "cylindrical_block_with_features"
export_step(part, "output.step")