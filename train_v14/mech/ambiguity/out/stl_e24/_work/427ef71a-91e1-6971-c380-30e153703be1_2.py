from build123d import *

outer_width = 50.0
outer_length = 60.0
outer_height = 30.0
wall_thickness = 5.0
slot_width = 3.0
slot_height = 15.0
chamfer_size = 1.0
hole_diameter = 4.0

solid_body = Box(outer_width, outer_length, outer_height)
solid_body = solid_body - Box(outer_width - 2*wall_thickness, outer_length - 2*wall_thickness, outer_height)
solid_body = solid_body - Pos(0, -outer_length/2 + wall_thickness/2, -outer_height/2 + slot_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - Cylinder(hole_diameter/2, outer_height)

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_slot"
export_step(part, "output.step")