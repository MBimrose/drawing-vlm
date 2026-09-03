from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_width = 30.0
vent_height = 10.0
vent_depth = 2.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
mount_hole_rows = 2
mount_hole_cols = 2
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 12.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(0, outer_width/2 - vent_depth/2, outer_height/2) * Box(vent_width, vent_depth, vent_height)
solid_body = solid_body - vent_cut

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols-1)/2) * mount_hole_spacing_x
        y = (j - (mount_hole_rows-1)/2) * mount_hole_spacing_y
        hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
        solid_body = solid_body - hole

rib_count = int((outer_width - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    y_pos = (i - (rib_count-1)/2) * rib_spacing
    rib = Pos(0, y_pos, outer_height - wall_thickness - rib_height/2) * Box(outer_length - 2*wall_thickness, rib_thickness, rib_height)
    solid_body = solid_body + rib

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")