from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 40.0
wall_thickness = 2.0
slot_width = 6.0
slot_height = 10.0
slot_spacing = 12.0
num_slots = 3
chamfer_distance = 0.5
mount_hole_diameter = 3.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 20.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(num_slots):
    x_pos = (i - (num_slots-1)/2) * slot_spacing
    slot = Pos(x_pos, 0, outer_height - wall_thickness - slot_height/2) * Box(slot_width, outer_width + 10, slot_height)
    solid_body = solid_body - slot

y_face = solid_body.faces().sort_by(Axis.Y)[-1]
y_edges = y_face.edges().filter_by(Axis.X)
solid_body = chamfer(y_edges, chamfer_distance)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_slots"
export_step(part, "output.step")