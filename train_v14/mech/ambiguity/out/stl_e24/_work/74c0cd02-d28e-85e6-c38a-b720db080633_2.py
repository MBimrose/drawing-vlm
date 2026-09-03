from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness
rib_spacing = 20.0
mount_hole_diameter = 5.0
mount_hole_offset_x = 20.0
mount_hole_offset_y = 15.0
slot_width = 5.0
slot_height = 15.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_count = int((inner_length - rib_spacing) // rib_spacing) + 1
rib_positions = [(-inner_length/2 + rib_spacing/2 + i * rib_spacing) for i in range(rib_count)]
for x in rib_positions:
    rib = Pos(x, 0, wall_thickness + rib_height/2) * Box(rib_thickness, inner_width, rib_height)
    solid_body = solid_body + rib

hole_positions = [
    (mount_hole_offset_x, mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, -mount_hole_offset_y)
]
for hx, hy in hole_positions:
    solid_body = solid_body - Pos(hx, hy, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

slot = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2 - slot_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "ribbed_enclosure_with_slot"
export_step(part, "output.step")