from build123d import *

bracket_length = 70.0
bracket_width = 60.0
bracket_thickness = 20.0
wall_thickness = 2.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-bracket_width/2, 0), (bracket_width/2, 0))
            l2 = Line(l1@1, (bracket_width/4, bracket_length*0.6))
            arc = ThreePointArc(l2@1, (0, bracket_length), (-bracket_width/4, bracket_length*0.6))
            l3 = Line(arc@1, (-bracket_width/2, 0))
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

part = solid_body
part.name = "bracket"
export_step(part, "output.step")