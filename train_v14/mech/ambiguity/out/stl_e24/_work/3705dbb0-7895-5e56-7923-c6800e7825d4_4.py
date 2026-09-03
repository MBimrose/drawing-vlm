from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
pocket_depth = 12.0
pocket_margin = 4.0
vent_hole_diameter = 1.5
vent_spacing = 10.0
vent_rows = 4
vent_cols = 7
mount_hole_diameter = 3.0
mount_hole_offset = 10.0
chamfer_size = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
pocket_length = inner_length - 2 * pocket_margin
pocket_width = inner_width - 2 * pocket_margin

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

bottom_plate = Pos(0, 0, wall_thickness/2) * Box(inner_length, inner_width, wall_thickness)
base = base + bottom_plate

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing
        y = (j - (vent_rows-1)/2) * vent_spacing
        base = base - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height + 10)

for sign in [1, -1]:
    base = base - Pos(sign * outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "ventilated_box"
export_step(part, "output.step")