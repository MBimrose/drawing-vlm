from build123d import *

outer_width = 80.0
outer_depth = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 20.0
vent_slot_spacing = 8.0
vent_slot_count = 7
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
fillet_radius = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:4]
solid_body = fillet(bottom_edges, fillet_radius)

for i in range(vent_slot_count):
    x = (i - (vent_slot_count - 1) / 2) * vent_slot_spacing
    slot = Pos(x, -outer_depth/2 + wall_thickness/2, outer_height/2 + wall_thickness + vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - slot

for i in range(2):
    for j in range(2):
        x = (i - 0.5) * mount_hole_spacing
        y = (j - 0.5) * mount_hole_spacing
        hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
        solid_body = solid_body - hole

for i in range(2):
    x = (i - 0.5) * (outer_width - 2 * wall_thickness)
    recess = Pos(x, outer_depth/2 - wall_thickness/2, outer_height/2) * Box(outer_width - 2 * wall_thickness, wall_thickness, outer_height - 2 * wall_thickness)
    solid_body = solid_body - recess

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")