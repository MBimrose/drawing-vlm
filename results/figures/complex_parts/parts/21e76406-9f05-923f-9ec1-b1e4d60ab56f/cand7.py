from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 6.0
rib_height = 48.0
rib_base = 12.0
rib_top = 4.0
hole_diameter = 5.0
cbore_diameter = 7.5
cbore_depth = 2.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness),
                     (thickness, thickness), (thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

for x, y in [(leg_length/3, thickness/2), (2*leg_length/3, thickness/2)]:
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

for x, y in [(thickness/2, leg_height/3), (thickness/2, 2*leg_height/3)]:
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

with BuildPart() as rib_p:
    with BuildSketch(Plane.YZ) as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_base, 0), (rib_top, rib_height), (0, rib_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = solid_body + rib_p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "L_bracket_with_rib"
export_step(part, "output.step")