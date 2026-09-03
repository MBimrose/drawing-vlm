from build123d import *

outer_radius = 20.0
wall_thickness = 3.0
length = 80.0
inlet_diameter = 8.0
chamfer_size = 1.0
slot_width = 4.0
slot_length = 30.0
slot_depth = 2.0
tab_width = 10.0
tab_height = 6.0
tab_thickness = 2.0

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole = Pos(0, 0, length/2) * Rot(0, 90, 0) * Cylinder(inlet_diameter/2, outer_radius*2)
solid_body = solid_body - hole

slot = Pos(outer_radius - slot_depth/2, 0, -length/2 + slot_length/2) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot

tab = Pos(outer_radius + tab_thickness/2, 0, -length/4) * Box(tab_thickness, tab_height, tab_width)
solid_body = solid_body + tab

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_hole_slot_tab"
export_step(part, "output.step")