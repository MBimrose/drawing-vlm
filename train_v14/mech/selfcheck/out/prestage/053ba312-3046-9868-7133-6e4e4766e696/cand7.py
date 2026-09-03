from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
rib_height = 6.0
rib_thickness = 4.0
rib_count = 6
fillet_radius = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
pocket_width = 40.0
pocket_depth = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

shell = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = shell.faces().sort_by(Axis.Z)[-1]
shell = chamfer(top_face.edges(), chamfer_distance)

bottom_face = shell.faces().sort_by(Axis.Z)[0]
shell = fillet(bottom_face.edges(), fillet_radius)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

shell = shell + ribs

hole = Cylinder(mount_hole_diameter / 2.0, length + 2.0)
shell = shell - Pos(mount_hole_spacing / 2.0, 0, 0) * hole
shell = shell - Pos(-mount_hole_spacing / 2.0, 0, 0) * hole

pocket = Pos(0, 0, length - pocket_depth / 2.0) * Box(pocket_width, pocket_width, pocket_depth)
shell = shell - pocket

part = shell
part.name = "ribbed_shell_with_pocket"
export_step(part, "output.step")