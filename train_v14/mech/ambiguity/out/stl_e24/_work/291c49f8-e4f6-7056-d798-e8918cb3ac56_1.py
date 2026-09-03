from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 20.0
vent_slot_spacing = 8.0
vent_slot_count = 7
mount_hole_diameter = 3.0
mount_hole_spacing_x = 20.0
mount_hole_spacing_y = 20.0
mount_hole_rows = 2
mount_hole_cols = 2
chamfer_size = 0.5
pocket_depth = 5.0
pocket_width = 30.0
pocket_length = 50.0

solid_body = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

pocket = Pos(0, 0, enclosure_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

vent_cut = Pos(0, enclosure_width/2 - wall_thickness/2, enclosure_height/2) * Box(enclosure_length * 0.6, wall_thickness, vent_slot_height)
solid_body = solid_body - vent_cut

for i in range(vent_slot_count):
    x = (i - (vent_slot_count - 1) / 2) * vent_slot_spacing
    slot = Pos(x, -enclosure_width/2 + wall_thickness/2, enclosure_height/2 + vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - slot

for i in range(mount_hole_cols):
    for j in range(mount_hole_rows):
        x = (i - (mount_hole_cols - 1) / 2) * mount_hole_spacing_x
        y = (j - (mount_hole_rows - 1) / 2) * mount_hole_spacing_y
        hole = Pos(x, y, enclosure_height/2) * Cylinder(mount_hole_diameter/2, enclosure_height)
        solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "enclosure"
export_step(part, "output.step")