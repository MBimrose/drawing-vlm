from build123d import *

panel_width = 80.0
panel_height = 100.0
panel_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
cutout_corner_radius = 5.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 3
hole_columns = 2
hole_margin_x = 15.0
hole_margin_y = 10.0
rib_width = 6.0
rib_height = 20.0
rib_spacing = 25.0
chamfer_distance = 1.0

solid_body = Box(panel_width, panel_height, panel_thickness)

with BuildPart() as cutout_bp:
    with BuildSketch() as cutout_sk:
        RectangleRounded(cutout_width, cutout_height, cutout_corner_radius)
    extrude(amount=panel_thickness * 2, both=True)
solid_body = solid_body - cutout_bp.part

for col in range(hole_columns):
    x = -panel_width/2 + hole_margin_x + col * (panel_width - 2 * hole_margin_x) / (hole_columns - 1)
    for row in range(hole_rows):
        y = -panel_height/2 + hole_margin_y + row * hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

rib_count = int((panel_height - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -panel_height/2 + rib_spacing + i * rib_spacing
    rib = Pos(-panel_width/2 + rib_width/2, y_pos, 0) * Box(rib_width, rib_height, panel_thickness)
    solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
outer_edges = [e for e in vertical_edges if abs(e.center().X) > panel_width/2 - 0.1 or abs(e.center().Y) > panel_height/2 - 0.1]
solid_body = chamfer(outer_edges, chamfer_distance)

part = solid_body
part.name = "panel_with_cutout_holes_and_ribs"
export_step(part, "output.step")