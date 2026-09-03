from build123d import *

outer_diameter = 60.0
wall_thickness = 8.0
length = 30.0
split_gap = 2.0
pocket_width = 20.0
pocket_depth = 6.0
pocket_height = 6.0
pocket_chamfer = 0.5
mount_hole_dia = 5.0
mount_hole_spacing = 40.0
rib_thickness = 2.0
rib_height = 5.0
rib_count = 4

inner_diameter = outer_diameter - 2 * wall_thickness
inner_radius = inner_diameter / 2.0
outer_radius = outer_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

split_cut = Pos(inner_radius - split_gap / 2.0, 0, 0) * Box(split_gap, length, length)
solid_body = solid_body - split_cut

pocket = Pos(0, outer_radius - pocket_depth / 2.0, 0) * Box(pocket_width, pocket_depth, pocket_height)
pocket = chamfer(pocket.edges(), pocket_chamfer)
solid_body = solid_body - pocket

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2.0, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
    solid_body = solid_body + rib

part = solid_body
part.name = "split_cylinder_with_pocket"
export_step(part, "output.step")