from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 20.0
vent_slot_spacing = 8.0
vent_slot_count = 7
cable_slot_width = 2.0
cable_slot_length = 40.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vent_start_x = -((vent_slot_count - 1) * vent_slot_spacing) / 2
for i in range(vent_slot_count):
    x = vent_start_x + i * vent_slot_spacing
    vent_cut = Pos(x, -outer_width/2 + wall_thickness/2, outer_height/2 + vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - vent_cut

cable_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(cable_slot_length, wall_thickness, outer_height)
solid_body = solid_body - cable_cut

for dx in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    for dy in [-mount_hole_spacing/2, mount_hole_spacing/2]:
        hole = Pos(dx, dy, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
        solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")