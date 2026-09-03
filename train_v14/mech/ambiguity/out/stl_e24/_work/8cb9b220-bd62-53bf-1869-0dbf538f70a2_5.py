from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_slot_offset = 0.0
mount_hole_diameter = 2.0
mount_hole_spacing = 30.0
chamfer_distance = 0.8
fillet_radius = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2 + vent_slot_offset) * Box(vent_slot_width, wall_thickness, vent_slot_height)
solid_body = solid_body - vent_cut

for y_pos in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y_pos, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)
    solid_body = solid_body - hole

x_face = solid_body.faces().sort_by(Axis.X)[-1]
solid_body = chamfer(x_face.edges(), chamfer_distance)

x_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = fillet(x_face.edges(), fillet_radius)

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")