from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_height = 3.0
rib_thickness = 1.5
vent_hole_diameter = 1.5
vent_rows = 4
vent_cols = 7
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
chamfer_distance = 0.5
pocket_depth = 4.0
pocket_margin = 5.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, rib_height/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, rib_height)
solid_body = solid_body + rib

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height + 10)

solid_body = solid_body - Pos(outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)
solid_body = solid_body - Pos(-outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(outer_length - 2*pocket_margin, outer_width - 2*pocket_margin, pocket_depth)
solid_body = solid_body - pocket

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")