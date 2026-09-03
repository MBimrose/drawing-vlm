from build123d import *

panel_width = 100
panel_height = 60
panel_thickness = 4
notch_width = 20
notch_depth = 15
hole_diameter = 5
hole_spacing = 15
hole_count = 5
fillet_radius = 2

with BuildPart() as p:
    with BuildSketch() as s:
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

solid = p.part
solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid = solid - Pos(x, 0, 0) * Cylinder(hole_diameter/2, panel_thickness * 2)

part = solid
part.name = "notched_panel_with_holes"
export_step(part, "output.step")