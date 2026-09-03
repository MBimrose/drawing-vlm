from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
mount_hole_rows = 2
mount_hole_cols = 2
tab_width = 10.0
tab_length = 20.0
tab_thickness = 5.0
rib_thickness = 4.0
rib_height = 6.0
rib_length = length
set_screw_diameter = 8.0
set_screw_offset = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size / 2.0)

tab = Pos(0, 0, length / 2 + tab_thickness / 2) * Box(tab_width, tab_length, tab_thickness)
solid_body = solid_body + tab

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2) * mount_hole_spacing
        y = (j - (mount_hole_rows - 1) / 2) * mount_hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, length + tab_thickness + 10)

rib = Pos(inner_radius - rib_height / 2, 0, 0) * Box(rib_height, rib_thickness, rib_length)
solid_body = solid_body + rib

solid_body = solid_body - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_diameter / 2, length + tab_thickness + 10)

part = solid_body
part.name = "hollow_cylinder_with_tab"
export_step(part, "output.step")