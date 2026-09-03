from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 4.0
vent_hole_diameter = 1.5
vent_rows = 4
vent_cols = 7
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
pocket_depth = 4.0
pocket_margin = 8.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Box(rib_thickness, outer_width - 2*wall_thickness, rib_height)
rib1 = Pos(-(outer_length/2 - wall_thickness - rib_thickness/2), 0, wall_thickness + rib_height/2) * rib
rib2 = Pos(outer_length/2 - wall_thickness - rib_thickness/2, 0, wall_thickness + rib_height/2) * rib
base = base + rib1 + rib2

pocket = Box(outer_length - 2*pocket_margin, outer_width - 2*pocket_margin, pocket_depth)
base = base - Pos(0, 0, outer_height - pocket_depth/2) * pocket

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        base = base - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height + 1)

mount_hole = Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 1)
base = base - Pos(-outer_length/2, 0, outer_height/2) * mount_hole
base = base - Pos(outer_length/2, 0, outer_height/2) * mount_hole

part = base
part.name = "ventilated_box_with_ribs"
export_step(part, "output.step")