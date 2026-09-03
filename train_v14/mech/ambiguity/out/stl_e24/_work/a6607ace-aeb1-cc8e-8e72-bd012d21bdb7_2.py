from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_slot_spacing = 14.0
vent_slot_count = 2
vent_hole_width = 1.0
vent_hole_height = 6.0
vent_hole_spacing = 8.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_depth = wall_thickness + 0.2
for i in range(vent_slot_count):
    z_pos = outer_height/2 + (i - (vent_slot_count-1)/2) * vent_slot_spacing
    solid_body = solid_body - Pos(outer_length/2 - slot_depth/2, 0, z_pos) * Box(slot_depth, vent_slot_width, vent_slot_height)
    solid_body = solid_body - Pos(-outer_length/2 + slot_depth/2, 0, z_pos) * Box(slot_depth, vent_slot_width, vent_slot_height)
    solid_body = solid_body - Pos(0, outer_width/2 - slot_depth/2, z_pos) * Box(vent_slot_width, slot_depth, vent_slot_height)
    solid_body = solid_body - Pos(0, -outer_width/2 + slot_depth/2, z_pos) * Box(vent_slot_width, slot_depth, vent_slot_height)

nx = int((outer_length - 2*wall_thickness) // vent_hole_spacing)
ny = int((outer_height - 2*wall_thickness) // vent_hole_spacing)
for i in range(nx):
    for j in range(ny):
        x_pos = (i - (nx-1)/2) * vent_hole_spacing
        z_pos = outer_height/2 + (j - (ny-1)/2) * vent_hole_spacing
        solid_body = solid_body - Pos(x_pos, outer_width/2 - wall_thickness/2, z_pos) * Box(vent_hole_width, wall_thickness, vent_hole_height)
        solid_body = solid_body - Pos(x_pos, -outer_width/2 + wall_thickness/2, z_pos) * Box(vent_hole_width, wall_thickness, vent_hole_height)

nx = int((outer_width - 2*wall_thickness) // vent_hole_spacing)
ny = int((outer_height - 2*wall_thickness) // vent_hole_spacing)
for i in range(nx):
    for j in range(ny):
        y_pos = (i - (nx-1)/2) * vent_hole_spacing
        z_pos = outer_height/2 + (j - (ny-1)/2) * vent_hole_spacing
        solid_body = solid_body - Pos(outer_length/2 - wall_thickness/2, y_pos, z_pos) * Box(wall_thickness, vent_hole_width, vent_hole_height)
        solid_body = solid_body - Pos(-outer_length/2 + wall_thickness/2, y_pos, z_pos) * Box(wall_thickness, vent_hole_width, vent_hole_height)

part = solid_body
part.name = "vented_box"
export_step(part, "output.step")