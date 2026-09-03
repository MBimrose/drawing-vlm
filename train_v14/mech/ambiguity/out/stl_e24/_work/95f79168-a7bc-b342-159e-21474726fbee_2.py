from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
mount_hole_rows = 2
mount_hole_cols = 2
rib_width = 4.0
rib_height = 6.0
rib_spacing = 20.0
lub_hole_diameter = 8.0
lub_hole_offset = 30.0
top_rib_width = 10.0
top_rib_length = 20.0
top_rib_height = 5.0

solid_body = Cylinder(outer_diameter / 2.0, length) - Cylinder(inner_diameter / 2.0, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2.0) * mount_hole_spacing
        y = (j - (mount_hole_rows - 1) / 2.0) * mount_hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2.0, length)

solid_body = solid_body - Pos(lub_hole_offset, 0, 0) * Cylinder(lub_hole_diameter / 2.0, length)

rib_count = int((outer_diameter - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_diameter / 2.0 + wall_thickness / 2.0, 0, 0) * Box(rib_width, rib_height, length)
    solid_body = solid_body + rib

top_rib = Pos(0, 0, length / 2.0 + top_rib_height / 2.0) * Box(top_rib_width, top_rib_length, top_rib_height)
solid_body = solid_body + top_rib

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")