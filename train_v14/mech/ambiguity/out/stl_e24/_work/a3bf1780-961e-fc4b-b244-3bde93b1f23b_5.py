from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
vent_width = 30.0
vent_height = 10.0
mount_hole_dia = 2.0
mount_hole_offset = 5.0
rib_width = 6.0
rib_height = 10.0
rib_thickness = 1.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(inner_length, inner_width, base_thickness)
solid_body = solid_body + base_plate

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent_cut

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)

rib1 = Pos(-inner_length/2 + rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
rib2 = Pos(inner_length/2 - rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")