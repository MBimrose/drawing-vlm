from build123d import *

tray_length = 100.0
tray_width = 60.0
tray_height = 16.0
wall_thickness = 2.0
base_thickness = 4.0
slot_width = 30.0
slot_depth = 2.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_count = 5
hole_offset_from_edge = 8.0
chamfer_size = 0.5

solid_body = Box(tray_length, tray_width, tray_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

base_plate = Pos(0, 0, -tray_height/2 + base_thickness/2) * Box(tray_length - 2*wall_thickness, tray_width - 2*wall_thickness, base_thickness)
solid_body = solid_body + base_plate

slot = Pos(0, tray_width/2 - slot_depth/2, tray_height/2) * Box(slot_width, slot_depth, tray_height)
solid_body = solid_body - slot

for i in range(hole_count):
    y_pos = -tray_width/2 + hole_offset_from_edge + i * hole_spacing
    x_pos = -tray_length/2 + hole_offset_from_edge
    hole = Pos(x_pos, y_pos, 0) * Cylinder(hole_diameter/2, tray_height)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "tray"
export_step(part, "output.step")