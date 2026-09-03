from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
chamfer_distance = 1.0
hole_diameter = 12.0
hole_spacing = 60.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
rib_width = 10.0
rib_height = 10.0
rib_thickness = 4.0

solid = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_distance)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid = solid - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid = solid - Pos(-outer_length/2, y, outer_height/2 - mount_hole_spacing/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

rib = Pos(0, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
solid = solid + rib

part = solid
part.name = "enclosure_with_rib"
export_step(part, "output.step")