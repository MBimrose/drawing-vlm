from build123d import *

bracket_width = 80.0
bracket_height = 50.0
bracket_thickness = 12.0
gusset_width = 20.0
gusset_height = 20.0
hole_diameter = 6.0
hole_spacing = 25.0
chamfer_distance = 5.0
rib_width = 6.0
rib_height = 10.0
rib_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline(
                (-bracket_width/2, -bracket_height/2),
                (bracket_width/2, -bracket_height/2),
                (bracket_width/2, bracket_height/2 - gusset_height),
                (bracket_width/2 - gusset_width, bracket_height/2),
                (-bracket_width/2, bracket_height/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

for x, y in [(-rib_spacing/2, 0), (rib_spacing/2, 0)]:
    rib = Pos(x, y, -bracket_thickness/4) * Box(rib_width, rib_height, bracket_thickness/2)
    solid_body = solid_body + rib

part = solid_body
part.name = "bracket_with_gusset_ribs"
export_step(part, "output.step")