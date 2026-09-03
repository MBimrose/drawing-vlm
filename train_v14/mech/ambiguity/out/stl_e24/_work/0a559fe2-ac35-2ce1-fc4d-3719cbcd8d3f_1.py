from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
vent_width = 40.0
vent_height = 20.0
vent_depth = 5.0
chamfer_size = 1.0
mount_hole_dia = 3.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = 20.0
rib_count = int((outer_length - 2 * wall_thickness) // rib_spacing)

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vent_cut = Pos(0, outer_width/2 - vent_depth/2, outer_height/2) * Box(vent_width, vent_depth, vent_height)
solid_body = solid_body - vent_cut

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(front_face.edges(), chamfer_size)

hole1 = Pos(outer_length/2, -mount_hole_spacing/2, outer_height/2 + mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
hole2 = Pos(outer_length/2, mount_hole_spacing/2, outer_height/2 + mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
solid_body = solid_body - hole1 - hole2

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")