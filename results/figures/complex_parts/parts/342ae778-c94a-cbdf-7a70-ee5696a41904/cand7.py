from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
relief_groove_width = 5.0
relief_groove_depth = 3.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
mount_hole_offset = 10.0
rib_width = 8.0
rib_height = 5.0
rib_thickness = 2.0
rib_spacing = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
wall_thickness = outer_radius - inner_radius

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)
result = result - Pos(0, 0, length/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)
result = result - Pos(0, 0, length/2 - relief_groove_depth/2) * Cylinder(inner_radius - relief_groove_width, relief_groove_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

mount_points = [
    (-mount_hole_spacing/2, -mount_hole_offset),
    (mount_hole_spacing/2, -mount_hole_offset),
    (-mount_hole_spacing/2, mount_hole_offset),
    (mount_hole_spacing/2, mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, length)

num_ribs = int(length // rib_spacing)
for i in range(num_ribs):
    angle = i * 360.0 / num_ribs
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
    result = result + rib

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")