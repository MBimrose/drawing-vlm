from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rim_height = 4.0
vent_hole_diameter = 1.5
vent_rows = 4
vent_cols = 7
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
chamfer_distance = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rim = Pos(0, 0, outer_height - rim_height/2) * (Box(outer_length, outer_width, rim_height) - Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, rim_height))

result = base + rim

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        result = result - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height)

result = result - Pos(-outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)

part = result
part.name = "ventilated_box"
export_step(part, "output.step")