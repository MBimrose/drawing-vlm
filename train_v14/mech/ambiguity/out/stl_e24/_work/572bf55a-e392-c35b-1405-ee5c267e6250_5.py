from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 5.0
corner_fillet_radius = 4.0
hole_diameter = 7.0
hole_spacing = 8.0
hole_count = 9
hole_row_y = -panel_height/4
blind_hole_diameter = 16.0
blind_hole_depth = 2.5
chamfer_distance = 0.5
tab_width = 20.0
tab_height = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(panel_width, panel_height)
    extrude(amount=panel_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

for i in range(hole_count):
    x = -((hole_count-1)/2)*hole_spacing + i*hole_spacing
    solid_body = solid_body - Pos(x, hole_row_y, panel_thickness/2) * Cylinder(hole_diameter/2, panel_thickness + 1)

solid_body = solid_body - Pos(0, 0, panel_thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

solid_body = solid_body + Pos(panel_width/2 - tab_width/2, 0, panel_thickness/2) * Box(tab_width, tab_height, panel_thickness)

part = solid_body
part.name = "panel_with_holes_and_tab"
export_step(part, "output.step")