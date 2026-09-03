from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 3.0
corner_fillet_radius = 5.0
slot_width = 6.0
slot_length = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
solid_body = solid_body - Box(inner_length, inner_width, outer_height)

slot_box = Box(slot_width, slot_width, slot_length)
solid_body = solid_body - Pos(outer_length/2 - slot_width/2, slot_width/2, 0) * slot_box
solid_body = solid_body - Pos(-outer_length/2 + slot_width/2, slot_width/2, 0) * slot_box

hole_cyl = Cylinder(mount_hole_diameter/2, outer_height)
for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * hole_cyl

part = solid_body
part.name = "hollow_box_with_slots_and_holes"
export_step(part, "output.step")