from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 3.0
hole_diameter = 11.0
hole_spacing = 12.0
hole_count = 6
hole_start_x = -((hole_count - 1) * hole_spacing) / 2.0
rib_width = 8.0
rib_height = 30.0
rib_thickness = 3.0
slot_width = 20.0
slot_height = 10.0
slot_offset_x = -panel_width / 2 + 15.0

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

rib = Pos(-panel_width / 2 + rib_width / 2, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

slot = Pos(slot_offset_x, 0, 0) * Box(slot_width, slot_height, panel_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    x = hole_start_x + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, panel_thickness / 2) * Cylinder(hole_diameter / 2, panel_thickness + 1)

part = solid_body
part.name = "panel_with_rib_slot_holes"
export_step(part, "output.step")