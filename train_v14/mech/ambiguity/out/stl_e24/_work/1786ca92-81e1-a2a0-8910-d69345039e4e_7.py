from build123d import *

body_length = 80.0
body_diameter = 40.0
wall_thickness = 3.0
inlet_diameter = 8.0
inlet_offset = 20.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
tab_width = 12.0
tab_height = 6.0
tab_thickness = 3.0
tab_offset = 30.0

solid_body = Cylinder(body_diameter / 2, body_length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

inlet_hole = Pos(0, 0, inlet_offset) * Rot(0, 90, 0) * Cylinder(inlet_diameter / 2, body_diameter + 2 * wall_thickness)
solid_body = solid_body - inlet_hole

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    mount_hole = Pos(x, 0, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, body_diameter + 2 * wall_thickness)
    solid_body = solid_body - mount_hole

tab = Pos(body_diameter / 2 + tab_thickness / 2, 0, tab_offset - body_length / 2) * Box(tab_thickness, tab_height, tab_width)
solid_body = solid_body + tab

part = solid_body
part.name = "hollow_cylinder_with_holes_and_tab"
export_step(part, "output.step")