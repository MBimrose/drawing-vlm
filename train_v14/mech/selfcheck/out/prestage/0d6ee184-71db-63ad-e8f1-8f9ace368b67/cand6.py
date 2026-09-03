from build123d import *

base_width = 70.0
base_height = 30.0
base_thickness = 10.0
tab_width = 40.0
tab_height = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0
hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as bl:
            Polyline(
                (-base_width/2, -base_height/2),
                (base_width/2, -base_height/2),
                (base_width/2, base_height/2),
                (tab_width/2, base_height/2),
                (tab_width/2, base_height/2 + tab_height),
                (-tab_width/2, base_height/2 + tab_height),
                (-tab_width/2, base_height/2),
                (-base_width/2, base_height/2),
                close=True
            )
        make_face()
    extrude(amount=base_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [
    (-hole_spacing/2, -base_height/2 + hole_offset_y),
    (hole_spacing/2, -base_height/2 + hole_offset_y),
    (0, base_height/2 + tab_height/2)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness + 2)

part = solid_body
part.name = "base_with_tab_and_holes"
export_step(part, "output.step")