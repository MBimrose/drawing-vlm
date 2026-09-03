from build123d import *

panel_length = 80.0
panel_width = 50.0
panel_thickness = 5.0
corner_fillet_radius = 3.0
hole_diameter = 11.0
hole_spacing = 12.0
hole_count = 6
hole_start_offset = 8.0
rib_width = 15.0
rib_height = 3.0
rib_thickness = 2.0
rib_offset_from_edge = 5.0
slot_length = 20.0
slot_width = 10.0
slot_offset_from_edge = 5.0

solid_body = Box(panel_length, panel_width, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

rib_y = panel_width/2 - rib_offset_from_edge - rib_width/2
rib = Pos(0, rib_y, rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

slot_x = -panel_length/2 + slot_offset_from_edge + slot_length/2
slot = Pos(slot_x, 0, 0) * Box(slot_length, slot_width, panel_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = -panel_length/2 + hole_start_offset + i * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "panel_with_rib_slot_holes"
export_step(part, "output.step")