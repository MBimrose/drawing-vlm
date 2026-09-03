from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_height = 4.0
rib_thickness = 2.0
vent_width = 40.0
vent_height = 12.0
vent_offset_z = 5.0
mount_hole_dia = 3.0
mount_hole_spacing_x = 25.0
mount_hole_spacing_y = 25.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
solid_body = chamfer(solid_body.edges(), chamfer_size)

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
cavity = Pos(0, 0, inner_height/2) * Box(inner_length, inner_width, inner_height)
solid_body = solid_body - cavity

rib = Pos(0, 0, -rib_height/2) * Box(inner_length, rib_thickness, rib_height)
solid_body = solid_body + rib

vent = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2 + vent_offset_z) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, outer_width/2 - wall_thickness/2, outer_height/2 + dy) * Cylinder(mount_hole_dia/2, wall_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "ventilated_box_with_rib"
export_step(part, "output.step")