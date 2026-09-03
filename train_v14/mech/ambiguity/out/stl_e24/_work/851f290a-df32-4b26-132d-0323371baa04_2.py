from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_slot_width = 30.0
vent_slot_height = 6.0
vent_slot_depth = wall_thickness * 0.6
mount_hole_diameter = 3.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
fillet_radius = 1.0
rib_thickness = 1.0
rib_height = 12.0
rib_length = 30.0
cable_cut_width = 4.0
cable_cut_height = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

vent_cut = Pos(-outer_length/2 + vent_slot_depth/2, 0, outer_height/2) * Box(vent_slot_depth, vent_slot_height, vent_slot_width)
solid_body = solid_body - vent_cut

cable_cut = Pos(0, 0, outer_height - wall_thickness/2) * Box(cable_cut_width, cable_cut_height, wall_thickness)
solid_body = solid_body - cable_cut

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, dy, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
        solid_body = solid_body - hole

rib = Pos(outer_length/2 + rib_thickness/2, 0, outer_height/2) * Box(rib_thickness, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")