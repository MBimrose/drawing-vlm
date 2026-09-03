from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 6.0
vent_slot_height = 1.0
vent_spacing = 8.0
vent_rows = 3
vent_columns = 10
connector_slot_width = 12.0
connector_slot_height = 5.0
connector_spacing = 15.0
connector_rows = 2
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

for i in range(vent_columns):
    for j in range(vent_rows):
        x = (i - (vent_columns-1)/2) * vent_spacing
        z = (j - (vent_rows-1)/2) * vent_spacing
        solid_body = solid_body - Pos(x, outer_width/2, z) * Box(vent_slot_height, vent_slot_width, vent_slot_width)
        solid_body = solid_body - Pos(x, -outer_width/2, z) * Box(vent_slot_height, vent_slot_width, vent_slot_width)
        solid_body = solid_body - Pos(x, z, outer_height/2) * Box(vent_slot_height, vent_slot_width, vent_slot_width)
        solid_body = solid_body - Pos(-x, z, outer_height/2) * Box(vent_slot_height, vent_slot_width, vent_slot_width)

for i in range(connector_rows):
    z = (i - (connector_rows-1)/2) * connector_spacing
    solid_body = solid_body - Pos(outer_length/2, 0, z) * Box(connector_slot_width, connector_slot_width, connector_slot_height)
    solid_body = solid_body - Pos(-outer_length/2, 0, z) * Box(connector_slot_width, connector_slot_width, connector_slot_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")