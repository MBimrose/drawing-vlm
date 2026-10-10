from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
bottom_thickness = 2.0
vent_hole_diameter = 1.5
vent_spacing_x = 10.0
vent_spacing_y = 10.0
vent_rows = 4
vent_cols = 7
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
chamfer_distance = 0.5
rib_height = 2.0
rib_thickness = 2.0
rib_offset = 4.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

bottom_plate = Pos(0, 0, bottom_thickness / 2) * Box(inner_length, inner_width, bottom_thickness)
solid_body = solid_body + bottom_plate

rib = Pos(0, inner_width / 2 - rib_offset, outer_height - wall_thickness - rib_height / 2) * Box(inner_length, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height / 2) * Cylinder(vent_hole_diameter / 2, outer_height)

solid_body = solid_body - Pos(outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length)
solid_body = solid_body - Pos(-outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")