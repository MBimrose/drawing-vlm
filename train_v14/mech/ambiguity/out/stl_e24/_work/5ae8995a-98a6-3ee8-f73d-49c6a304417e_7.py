from build123d import *

outer_diameter = 30.0
inner_diameter = 20.0
length = 70.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 4.0
slot_length = 50.0
slot_depth = wall_thickness * 0.6
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
solid_body = outer_cyl - inner_cyl

slot_box = Pos(0, outer_diameter / 2.0 - slot_depth / 2.0, 0) * Box(slot_width, slot_depth, slot_length)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

hole_cyl = Pos(0, outer_diameter / 2.0, mount_hole_offset) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, outer_diameter)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "hollow_cylinder_with_slot"
export_step(part, "output.step")