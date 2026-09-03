from build123d import *

outer_diameter = 30.0
inner_diameter = 20.0
length = 70.0
slot_width = 4.0
slot_length = 50.0
slot_depth = 3.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

slot_box = Pos(0, outer_radius - slot_depth/2.0, 0) * Box(slot_width, slot_depth, slot_length)
solid_body = solid_body - slot_box

hole_cyl = Pos(0, outer_radius, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_diameter)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "hollow_cylinder_with_slot_and_hole"
export_step(part, "output.step")