from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
rib_count = 6
rib_width = 6.0
rib_thickness = 4.0
fillet_radius = 2.0
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
slot_width = 6.0
slot_length = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_width, height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, height)

slot = Pos(0, 0, height - wall_thickness / 2) * Box(slot_length, slot_width, wall_thickness)
solid_body = solid_body - slot

part = solid_body
part.name = "ribbed_cylinder_with_holes"
export_step(part, "output.step")