from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.5
channel_width = 20.0
channel_depth = 10.0
fillet_radius = 1.2
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
counterbore_diameter = 8.0
counterbore_depth = 5.0
through_hole_diameter = 4.0

solid_body = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

channel_cut = Pos(0, 0, chute_height - channel_depth/2) * Box(chute_length - 2*wall_thickness, channel_width, channel_depth)
solid_body = solid_body - channel_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

rib_count = int((chute_length - 2*wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -chute_length/2 + wall_thickness + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

through_hole = Pos(0, 0, chute_height/2) * Cylinder(through_hole_diameter/2, chute_height + 10)
solid_body = solid_body - through_hole

counterbore = Pos(0, 0, chute_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - counterbore

part = solid_body
part.name = "chute"
export_step(part, "output.step")