from build123d import *

panel_width = 100.0
panel_height = 60.0
panel_thickness = 4.0
notch_width = 20.0
notch_depth = 15.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 5
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-panel_width/2, -panel_height/2),
                (panel_width/2, -panel_height/2),
                (panel_width/2, panel_height/2 - notch_depth),
                (panel_width/2 - notch_width, panel_height/2 - notch_depth),
                (panel_width/2 - notch_width, panel_height/2),
                (-panel_width/2, panel_height/2),
                close=True
            )
        make_face()
    extrude(amount=panel_thickness)

solid_body = p.part

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "panel_with_notch_and_holes"
export_step(part, "output.step")