from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
chamfer_size = 2.0
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
rib_width = 8.0
rib_height = 4.0
rib_count = 12
boss_diameter = 20.0
boss_height = 10.0

solid_body = Cylinder(outer_diameter / 2, length)
solid_body = solid_body - Cylinder(inner_diameter / 2, length)
solid_body = solid_body - Pos(0, 0, length / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, length)

solid_body = solid_body + Pos(0, 0, -length / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

rib = Pos(outer_diameter / 2 - rib_height / 2, 0, 0) * Box(rib_height, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")