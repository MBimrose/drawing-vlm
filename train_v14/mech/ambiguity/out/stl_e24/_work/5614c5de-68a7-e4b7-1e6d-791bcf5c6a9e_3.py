from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 3.0
corner_fillet_radius = 5.0
slot_width = 12.0
slot_height = 30.0
mount_hole_diameter = 3.0
mount_hole_offset = 8.0

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_box = Box(wall_thickness, slot_width, slot_height)
solid_body = solid_body - Pos(-outer_length/2 + wall_thickness/2, 0, 0) * slot_box
solid_body = solid_body - Pos(outer_length/2 - wall_thickness/2, 0, 0) * slot_box

hole_cyl = Cylinder(mount_hole_diameter/2, outer_height)
for x in [-outer_length/2 + mount_hole_offset, outer_length/2 - mount_hole_offset]:
    for y in [-outer_width/2 + mount_hole_offset, outer_width/2 - mount_hole_offset]:
        solid_body = solid_body - Pos(x, y, 0) * hole_cyl

part = solid_body
part.name = "hollow_box_with_slots_and_holes"
export_step(part, "output.step")