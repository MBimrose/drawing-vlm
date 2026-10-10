from build123d import *

outer_diameter = 70.0
length = 80.0
wall_thickness = 5.0
slot_width = 12.0
slot_depth = 8.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_width = 4.0
rib_height = 8.0
rib_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_depth)
result = result - slot_box

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2.0, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_height / 2.0, 0, 0) * Box(rib_width, rib_height, length - 2 * wall_thickness)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_slot_ribs"
export_step(part, "output.step")