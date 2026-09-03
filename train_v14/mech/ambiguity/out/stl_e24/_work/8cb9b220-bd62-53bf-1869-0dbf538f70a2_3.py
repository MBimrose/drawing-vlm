from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_width = 12.0
vent_height = 5.0
mount_hole_dia = 2.0
mount_hole_spacing = 30.0
chamfer_size = 0.8
fillet_radius = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner = offset(solid_body, amount=-wall_thickness)
solid_body = solid_body - inner

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent_cut

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length + 10)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")