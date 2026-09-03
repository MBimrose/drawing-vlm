from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
vent_hole_diameter = 4.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 15.0
vent_spacing_y = 10.0
chamfer_size = 1.0

outer = Box(outer_width, outer_depth, outer_height)
inner = Box(outer_width - 2*wall_thickness, outer_depth - 2*wall_thickness, outer_height)
result = outer - inner

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        z = (j - (vent_rows - 1) / 2) * vent_spacing_y
        result = result - Pos(x, outer_depth/2, z) * Rot(90, 0, 0) * Cylinder(vent_hole_diameter/2, outer_depth + 10)

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "ventilated_box"
export_step(part, "output.step")