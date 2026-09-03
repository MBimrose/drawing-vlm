from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_length = 60.0
vent_width = 30.0
vent_depth = 4.0
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(0, 0, outer_height - vent_depth/2) * Box(vent_length, vent_width, vent_depth)
solid_body = solid_body - vent_cut

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

rib_count = int((outer_width - 2*wall_thickness - rib_spacing) // (rib_spacing + rib_thickness))
for i in range(rib_count):
    y_pos = -outer_width/2 + wall_thickness + rib_spacing + i*(rib_spacing + rib_thickness) + rib_thickness/2
    rib = Pos(0, y_pos, outer_height - wall_thickness - rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "vented_enclosure"
export_step(part, "output.step")