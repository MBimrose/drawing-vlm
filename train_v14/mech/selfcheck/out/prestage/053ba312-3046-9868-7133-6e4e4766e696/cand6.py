from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
length = 60.0
groove_width = 12.0
groove_depth = 2.0
fillet_radius = 2.0
mount_hole_diameter = 6.0
mount_hole_offset = 15.0
rib_thickness = 4.0
rib_height = 6.0
rib_count = 6

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)
solid_body = fillet(solid_body.edges(), fillet_radius)

groove = Pos(0, 0, length/2 - groove_width/2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, length)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_groove_ribs"
export_step(part, "output.step")