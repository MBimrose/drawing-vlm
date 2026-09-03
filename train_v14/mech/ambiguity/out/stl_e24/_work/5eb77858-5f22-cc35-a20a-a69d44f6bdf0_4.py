from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 3.0
hole_diameter = 11.0
hole_spacing = 12.0
hole_count = 5
hole_start_x = -((hole_count - 1) * hole_spacing) / 2.0
slot_width = 20.0
slot_height = 10.0
slot_offset_x = -panel_width / 2 + slot_width / 2 + 5.0

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

slot = Pos(slot_offset_x, 0, 0) * Box(slot_width, slot_height, panel_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = hole_start_x + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, panel_thickness)

part = solid_body
part.name = "panel_with_slot_and_holes"
export_step(part, "output.step")