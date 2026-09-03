from build123d import *

overall_width = 80.0
overall_height = 40.0
length = 100.0
web_thickness = 5.0
flange_thickness = 5.0
chamfer_size = 2.0
hole_diameter = 8.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
vent_hole_diameter = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing = 12.0

inner_width = overall_width - web_thickness
inner_height = overall_height - 2 * flange_thickness
cavity_center_x = -overall_width / 2 + web_thickness + inner_width / 2
cavity_center_z = 0.0

result = Box(overall_width, length, overall_height)

cavity = Pos(cavity_center_x, 0, cavity_center_z) * Box(inner_width, length, inner_height)
result = result - cavity

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

hole = Pos(cavity_center_x, 0, cavity_center_z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, overall_width)
result = result - hole

pocket = Pos(-overall_width/2 + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
result = result - pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        y = (i - (vent_cols-1)/2) * vent_spacing
        z = (j - (vent_rows-1)/2) * vent_spacing
        vent = Pos(-overall_width/2 + web_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(vent_hole_diameter/2, web_thickness)
        result = result - vent

part = result
part.name = "channel_with_holes"
export_step(part, "output.step")