from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
base_thickness = 4.0
rim_height = 2.0
rim_thickness = 2.0
vent_hole_diameter = 1.5
vent_spacing_x = 10.0
vent_spacing_y = 10.0
vent_rows = 4
vent_cols = 7
mount_hole_diameter = 3.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

base_plate = Pos(0, 0, base_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

rim_outer = Pos(0, 0, outer_height - rim_height/2) * Box(outer_length, outer_width, rim_height)
rim_inner = Pos(0, 0, outer_height - rim_height/2) * Box(outer_length - 2*rim_thickness, outer_width - 2*rim_thickness, rim_height)
solid_body = solid_body + (rim_outer - rim_inner)

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height + 10)

solid_body = solid_body - Pos(-outer_length/2, 0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)
solid_body = solid_body - Pos(outer_length/2, 0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")