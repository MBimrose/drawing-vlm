from build123d import *

outer_diameter = 80
inner_diameter = 60
length = 70
wall_thickness = (outer_diameter - inner_diameter) / 2
slot_width = 10
slot_height = 30
slot_offset = 20
tab_width = 20
tab_height = 15
tab_thickness = 5
relief_width = 15
relief_height = 20
relief_depth = 8
hole_diameter = 5
hole_spacing = 30

outer_radius = outer_diameter / 2
inner_radius = inner_diameter / 2

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Pos(outer_radius - wall_thickness/2, 0, slot_offset) * Box(wall_thickness + 2, slot_width, slot_height)
solid_body = solid_body - slot_box

tab_box = Pos(outer_radius - tab_thickness/2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab_box

relief_box = Pos(inner_radius - relief_depth/2, 0, 0) * Box(relief_depth, relief_width, relief_height)
solid_body = solid_body - relief_box

hole1 = Pos(outer_radius - wall_thickness/2, 0, hole_spacing/2) * Cylinder(hole_diameter/2, wall_thickness + 2)
hole2 = Pos(outer_radius - wall_thickness/2, 0, -hole_spacing/2) * Cylinder(hole_diameter/2, wall_thickness + 2)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "hollow_cylinder_with_slot_tab_relief_holes"
export_step(part, "output.step")