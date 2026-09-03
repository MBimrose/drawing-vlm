from build123d import *

base_length = 70
base_width = 40
base_height = 20
rib_length = 50
rib_width = 12
rib_height = 8
central_hole_diameter = 10
mount_hole_diameter = 4
mount_hole_spacing = 30
fillet_radius = 2
chamfer_distance = 1

base = Box(base_length, base_width, base_height)
rib = Pos(0, 0, base_height/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = base + rib

solid_body = solid_body - Cylinder(central_hole_diameter/2, base_height + rib_height + 10)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, base_height/2 + rib_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, rib_width + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "base_with_rib_and_holes"
export_step(part, "output.step")