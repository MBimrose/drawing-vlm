from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 6.0
gusset_height = 40.0
gusset_width = 10.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as g:
    with BuildSketch(Plane.YZ) as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + g.part

for x, y in [(leg_length/3, thickness/2), (2*leg_length/3, thickness/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 10)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

for x, y in [(thickness/2, leg_length/3), (thickness/2, 2*leg_length/3)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 10)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")