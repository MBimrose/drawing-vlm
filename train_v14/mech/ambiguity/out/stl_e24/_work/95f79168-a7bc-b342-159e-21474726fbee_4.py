from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
mount_hole_count = 4
oil_hole_dia = 8.0
oil_hole_offset = 30.0
rib_thickness = 4.0
rib_height = 6.0
rib_spacing = 20.0
boss_width = 10.0
boss_length = 20.0
boss_height = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

result = result - Pos(oil_hole_offset, 0, 0) * Cylinder(oil_hole_dia / 2, length)

mount_points = [
    (mount_hole_spacing / 2, mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (mount_hole_spacing / 2, -mount_hole_spacing / 2),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, length)

rib1 = Pos(inner_radius + rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_thickness, rib_height)
rib2 = Pos(-(inner_radius + rib_thickness / 2), 0, 0) * Box(rib_thickness, rib_thickness, rib_height)
result = result + rib1 + rib2

boss = Pos(0, 0, length / 2 + boss_height / 2) * Box(boss_width, boss_length, boss_height)
result = result + boss

part = result
part.name = "bearing_housing"
export_step(part, "output.step")