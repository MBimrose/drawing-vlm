from build123d import *

base_width = 60.0
height = 70.0
thickness = 20.0
wall_thickness = 2.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-base_width/2, 0), (base_width/2, 0))
            l2 = Line(l1@1, (base_width/4, height*0.6))
            a1 = ThreePointArc(l2@1, (0, height), (-base_width/4, height*0.6))
            l3 = Line(a1@1, (-base_width/2, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

hole_positions = [
    (-base_width/2 + hole_offset, hole_offset),
    (base_width/2 - hole_offset, hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness*2)

part = solid_body
part.name = "shelled_profile_with_holes"
export_step(part, "output.step")