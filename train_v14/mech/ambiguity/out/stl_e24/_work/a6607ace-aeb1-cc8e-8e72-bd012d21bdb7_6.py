from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_slot_offset = 10.0
vent_slot_spacing = 15.0
vent_slot_count = 2
rib_thickness = 1.0
rib_height = 6.0
rib_spacing = 8.0

result = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = result.faces().sort_by(Axis.Z)[-1]
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = offset(result, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_slot = Box(vent_slot_width, wall_thickness, vent_slot_height)
for i in range(vent_slot_count):
    z_pos = outer_height/2 + (i - (vent_slot_count-1)/2) * vent_slot_spacing
    result = result - Pos(outer_length/2 - wall_thickness/2, 0, z_pos) * vent_slot
    result = result - Pos(-outer_length/2 + wall_thickness/2, 0, z_pos) * vent_slot

vent_slot_y = Box(wall_thickness, vent_slot_width, vent_slot_height)
for i in range(vent_slot_count):
    z_pos = outer_height/2 + (i - (vent_slot_count-1)/2) * vent_slot_spacing
    result = result - Pos(0, outer_width/2 - wall_thickness/2, z_pos) * vent_slot_y
    result = result - Pos(0, -outer_width/2 + wall_thickness/2, z_pos) * vent_slot_y

rib_count_x = int((outer_length - 2*wall_thickness) // rib_spacing)
rib = Box(rib_thickness, wall_thickness, rib_height)
for i in range(rib_count_x):
    x_pos = (i - (rib_count_x-1)/2) * rib_spacing
    result = result - Pos(x_pos, outer_width/2 - wall_thickness/2, wall_thickness + rib_height/2) * rib
    result = result - Pos(x_pos, -outer_width/2 + wall_thickness/2, wall_thickness + rib_height/2) * rib

part = result
part.name = "vented_box"
export_step(part, "output.step")