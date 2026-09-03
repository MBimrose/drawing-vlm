from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 4.0
rib_height = 12.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
vent_hole_diameter = 1.5
vent_rows = 4
vent_cols = 7
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
chamfer_size = 0.5

result = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = result.faces().sort_by(Axis.Z)[-1]
result = offset(result, amount=-wall_thickness, openings=[top_face])

rib1 = Pos(-outer_length/2 + wall_thickness + rib_thickness/2, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
rib2 = Pos(outer_length/2 - wall_thickness - rib_thickness/2, 0, wall_thickness + rib_height/2) * Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
result = result + rib1 + rib2

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        result = result - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height)

for sign in [-1, 1]:
    result = result - Pos(sign * outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "ventilated_box_with_ribs"
export_step(part, "output.step")