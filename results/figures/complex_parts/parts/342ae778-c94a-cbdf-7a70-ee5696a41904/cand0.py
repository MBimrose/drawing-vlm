from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
fillet_radius = 2.0
chamfer_distance = 1.5
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
mount_hole_offset = 10.0
rib_width = 8.0
rib_height = 5.0
rib_thickness = 3.0
rib_count = 12

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

solid_body = Cylinder(outer_radius, length)
solid_body = solid_body - Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

mount_points = [
    (mount_hole_spacing/2, mount_hole_offset),
    (-mount_hole_spacing/2, mount_hole_offset),
    (mount_hole_spacing/2, -mount_hole_offset),
    (-mount_hole_spacing/2, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, length)

rib = Pos(outer_radius - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "cylindrical_housing_with_ribs"
export_step(part, "output.step")