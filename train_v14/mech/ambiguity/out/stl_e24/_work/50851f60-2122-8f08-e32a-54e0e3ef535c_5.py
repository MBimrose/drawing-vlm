from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
height = 20.0
slot_width = 4.0
slot_length = 12.0
slot_depth = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

for i in range(4):
    angle = i * 90
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
    result = result - slot

for x, y in [(-mount_hole_spacing / 2.0, 0), (mount_hole_spacing / 2.0, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2.0, height)

pocket = Pos(0, 0, height / 2.0 - pocket_depth / 2.0) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")