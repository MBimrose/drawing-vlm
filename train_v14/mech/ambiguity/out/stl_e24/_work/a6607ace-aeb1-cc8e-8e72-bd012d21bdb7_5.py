from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 12.0
vent_rows = 2
vent_columns = 3
vent_spacing_x = 10.0
vent_spacing_y = 15.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
rib_thickness = 1.0
rib_height = 6.0
rib_spacing = 8.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_points = []
for i in range(vent_columns):
    for j in range(vent_rows):
        x = (i - (vent_columns-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        vent_points.append((x, y))

for x, y in vent_points:
    solid_body = solid_body - Pos(outer_length/2 - wall_thickness/2, x, outer_height/2 + y) * Box(wall_thickness, vent_slot_height, vent_slot_width)
    solid_body = solid_body - Pos(-outer_length/2 + wall_thickness/2, x, outer_height/2 + y) * Box(wall_thickness, vent_slot_height, vent_slot_width)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (outer_length - mount_hole_offset, mount_hole_offset),
    (mount_hole_offset, outer_width - mount_hole_offset),
    (outer_length - mount_hole_offset, outer_width - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, outer_height) * Cylinder(mount_hole_diameter/2, outer_height)

rib_count = int((outer_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count-1)/2) * rib_spacing
    solid_body = solid_body - Pos(x, outer_width/2 - wall_thickness/2, wall_thickness + rib_height/2) * Box(rib_thickness, wall_thickness, rib_height)
    solid_body = solid_body - Pos(x, -outer_width/2 + wall_thickness/2, wall_thickness + rib_height/2) * Box(rib_thickness, wall_thickness, rib_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")