from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 60.0
counterbore_diameter = 45.0
counterbore_depth = 15.0
chamfer_size = 2.0
knurl_width = 5.0
knurl_height = 8.0
knurl_depth = 2.0
knurl_spacing_deg = 15.0
mount_hole_diameter = 6.0
mount_hole_offset = 20.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_offset = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

solid_body = Cylinder(outer_radius, height)
solid_body = solid_body - Cylinder(inner_radius, height)
solid_body = solid_body - Pos(0, 0, height/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(-pocket_offset, 0, height/2 - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, height)

knurl_count = int(360 / knurl_spacing_deg)
for i in range(knurl_count):
    angle = i * knurl_spacing_deg
    rib = Rot(0, 0, angle) * Pos(outer_radius - knurl_depth/2, 0, knurl_depth/2) * Box(knurl_width, knurl_height, knurl_depth)
    solid_body = solid_body + rib

part = solid_body
part.name = "knurled_bushing"
export_step(part, "output.step")