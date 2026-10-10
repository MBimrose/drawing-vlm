from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 5.0
vent_hole_diameter = 1.5
vent_rows = 4
vent_cols = 7
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
mount_hole_offset = 10.0
chamfer_distance = 1.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

floor = Pos(0, 0, wall_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, wall_thickness)
base = base + floor

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        base = base - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height)

base = base - Pos(outer_length/2, 0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)
base = base - Pos(-outer_length/2, 0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_distance)

part = base
part.name = "ventilated_box"
export_step(part, "output.step")