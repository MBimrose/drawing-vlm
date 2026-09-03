from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
blind_hole_diameter = 16.0
blind_hole_depth = 2.5
through_hole_diameter = 7.0
through_hole_spacing = 8.0
through_hole_count = 9
rib_width = 6.0
rib_height = 3.0
rib_offset = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(panel_width, panel_height)
    extrude(amount=panel_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body - Pos(0, 0, panel_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

start_x = -((through_hole_count - 1) * through_hole_spacing) / 2
y_pos = -panel_height / 4
for i in range(through_hole_count):
    x_pos = start_x + i * through_hole_spacing
    solid_body = solid_body - Pos(x_pos, y_pos, panel_thickness/2) * Cylinder(through_hole_diameter/2, panel_thickness)

rib = Pos(0, panel_height/2 - rib_offset, panel_thickness/2) * Box(panel_width - 2*rib_offset, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "panel_with_rib_and_holes"
export_step(part, "output.step")