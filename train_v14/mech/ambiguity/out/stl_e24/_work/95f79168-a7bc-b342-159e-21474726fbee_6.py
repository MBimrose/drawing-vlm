from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
height = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_width = 10.0
rib_length = 20.0
rib_height = 5.0
slot_width = 4.0
slot_length = 12.0
slot_depth = 10.0
lub_hole_diameter = 8.0
lub_hole_offset = 30.0

solid_body = Cylinder(outer_diameter / 2.0, height) - Cylinder(inner_diameter / 2.0, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2), (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2), (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2.0, height)

solid_body = solid_body - Pos(lub_hole_offset, 0, 0) * Cylinder(lub_hole_diameter / 2.0, height)

slot_box = Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - Pos(outer_diameter/2 - slot_depth/2, 0, 0) * slot_box
solid_body = solid_body - Pos(-outer_diameter/2 + slot_depth/2, 0, 0) * slot_box

rib = Pos(0, 0, height/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_features"
export_step(part, "output.step")