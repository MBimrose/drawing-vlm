from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
chamfer_size = 1.0
hole_diameter = 12.0
hole_spacing = 60.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
mount_hole_offset = 5.0
rib_width = 10.0
rib_thickness = 4.0
rib_height = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

for y, z in [(-mount_hole_spacing/2, mount_hole_offset), (mount_hole_spacing/2, mount_hole_offset)]:
    solid_body = solid_body - Pos(-outer_length/2, y, z) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

rib = Pos(0, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "enclosure_with_rib"
export_step(part, "output.step")