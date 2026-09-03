from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
bottom_chamfer = 0.5
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 2.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
vent_slot_width = 5.0
vent_slot_height = 20.0
vent_slot_spacing = 8.0
vent_slot_count = 7

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:4]
solid_body = chamfer(bottom_edges, bottom_chamfer)

pocket = Pos(0, outer_width/2 - pocket_depth/2, outer_height/2) * Box(pocket_length, pocket_depth, pocket_width)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

for i in range(vent_slot_count):
    x = (i - (vent_slot_count-1)/2) * vent_slot_spacing
    slot = Pos(x, -outer_width/2 + wall_thickness/2, outer_height/2 + vent_slot_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")