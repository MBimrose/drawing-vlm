from build123d import *

panel_width = 80
panel_height = 50
panel_thickness = 5
corner_fillet_radius = 3
hole_diameter = 11
hole_spacing = 12
hole_count = 6
hole_start_x = -((hole_count - 1) * hole_spacing) / 2
rib_width = 8
rib_height = 30
rib_offset_x = -panel_width / 2 + rib_width / 2 + 5
notch_width = 20
notch_height = 10
notch_offset_x = -panel_width / 2 + notch_width / 2 + 5

solid_body = Box(panel_width, panel_height, panel_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

notch = Pos(notch_offset_x, 0, 0) * Box(notch_width, notch_height, panel_thickness)
solid_body = solid_body - notch

rib = Pos(rib_offset_x, 0, 0) * Box(rib_width, rib_height, panel_thickness)
solid_body = solid_body + rib

for i in range(hole_count):
    x = hole_start_x + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, panel_thickness)

part = solid_body
part.name = "panel_with_rib_and_holes"
export_step(part, "output.step")