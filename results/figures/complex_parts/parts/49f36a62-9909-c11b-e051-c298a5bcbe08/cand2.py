from build123d import *

inner_diameter = 19.6
wall_thickness = 9.2
outer_diameter = inner_diameter + 2 * wall_thickness
height = 15.0
rib_height = 2.0
rib_thickness = 1.0
slot_width = 0.8
slot_length = 12.0
slot_depth = 2.0
chamfer_size = 0.4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

rib = Pos(0, 0, height/2 + rib_height/2) * Box(rib_thickness, outer_diameter, rib_height)
solid_body = solid_body + rib

slot = Pos(0, 0, height/2 - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_rib_and_slot"
export_step(part, "output.step")