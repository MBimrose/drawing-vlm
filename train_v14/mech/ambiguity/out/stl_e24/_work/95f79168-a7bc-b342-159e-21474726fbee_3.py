from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
top_chamfer = 2.0
bottom_chamfer = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
cable_gland_diameter = 8.0
cable_gland_offset = 30.0
rib_width = 10.0
rib_height = 20.0
rib_thickness = 5.0
side_rib_thickness = 4.0
side_rib_height = 6.0
side_rib_length = 30.0

solid_body = Cylinder(outer_diameter / 2.0, length) - Cylinder(inner_diameter / 2.0, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), top_chamfer)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), bottom_chamfer)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2), (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2), (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2.0, length)

solid_body = solid_body - Pos(cable_gland_offset, 0, 0) * Cylinder(cable_gland_diameter / 2.0, length)

solid_body = solid_body + Pos(0, 0, length/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

solid_body = solid_body + Pos(-outer_diameter/2 + side_rib_thickness/2, 0, 0) * Box(side_rib_thickness, side_rib_thickness, side_rib_height)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")