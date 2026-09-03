from build123d import *

panel_width = 80.0
panel_height = 60.0
panel_thickness = 2.0
corner_radius = 5.0
notch_radius = 15.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 10.0
hole_offset_y = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-panel_width/2, -panel_height/2), (panel_width/2, -panel_height/2))
            l2 = Line(l1@1, (panel_width/2, panel_height/2 - corner_radius))
            arc = ThreePointArc(l2@1, (panel_width/2 - corner_radius, panel_height/2 - corner_radius), (panel_width/2 - corner_radius, panel_height/2))
            l3 = Line(arc@1, (-panel_width/2, panel_height/2))
            l4 = Line(l3@1, (-panel_width/2, -panel_height/2))
        make_face()
    extrude(amount=panel_thickness)

solid_body = p.part
solid_body = solid_body - Pos(panel_width/2, 0, 0) * Cylinder(notch_radius, panel_thickness * 2)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + i * hole_spacing
        y = hole_offset_y + j * hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "panel_with_notch_and_holes"
export_step(part, "output.step")