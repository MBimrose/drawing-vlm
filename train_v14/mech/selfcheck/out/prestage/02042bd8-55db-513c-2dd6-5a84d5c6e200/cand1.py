from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
chamfer_size = 1.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = outer_height - wall_thickness - 5.0
hole_diameter = 12.0
hole_spacing = 30.0
rib_height = 10.0
rib_thickness = 4.0
rib_length = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x in [-hole_spacing, hole_spacing]:
    solid_body = solid_body - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(-outer_length/2, y, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

rib = Pos(0, 0, outer_height/2) * Box(rib_length, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_box_with_pockets_and_ribs"
export_step(part, "output.step")