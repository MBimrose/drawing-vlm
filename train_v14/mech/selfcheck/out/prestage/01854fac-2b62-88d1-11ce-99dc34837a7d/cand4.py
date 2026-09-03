from build123d import *

panel_width = 80
panel_height = 100
panel_thickness = 5
cutout_width = 40
cutout_height = 30
cutout_fillet_radius = 5
hole_diameter = 4
hole_spacing = 12
hole_offset_x = 15
chamfer_distance = 1

solid_body = Box(panel_width, panel_height, panel_thickness)

with BuildPart() as cutout_bp:
    with BuildSketch() as cutout_sk:
        RectangleRounded(cutout_width, cutout_height, cutout_fillet_radius)
    extrude(amount=panel_thickness + 2)
solid_body = solid_body - cutout_bp.part

for x_offset in (-hole_offset_x, hole_offset_x):
    for i in range(3):
        y_pos = -hole_spacing + i * hole_spacing
        solid_body = solid_body - Pos(x_offset, y_pos, 0) * Cylinder(hole_diameter/2, panel_thickness + 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "panel_with_cutout_and_holes"
export_step(part, "output.step")