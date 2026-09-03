from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_width = 10.0
rib_height = 5.0
rib_spacing = 15.0
rib_count = 3
vent_slot_width = 4.0
vent_slot_length = 55.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_length = outer_length - 2 * wall_thickness
for i in range(rib_count):
    y_pos = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(0, y_pos, wall_thickness + rib_height + rib_height/2) * Box(rib_length, rib_width, rib_height)
    solid_body = solid_body + rib

vent = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_slot_length, wall_thickness, vent_slot_width)
solid_body = solid_body - vent

for x in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for y in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height + 10)
        solid_body = solid_body - hole

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_box_with_ribs"
export_step(part, "output.step")