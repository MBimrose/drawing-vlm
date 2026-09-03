from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
rib_thickness = 3.0
rib_width = 5.0
hole_diameter = 6.0
hole_spacing = 25.0
chamfer_dist = 1.0
pocket_radius = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length,0), (leg_length,leg_width), (leg_width,leg_width), (leg_width,leg_length), (0,leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

rib1 = Pos(leg_length/2, leg_width/2, thickness/4) * Box(leg_length - 2*rib_width, rib_thickness, thickness/2)
solid_body = solid_body + rib1

rib2 = Pos(leg_width/2, leg_length/2, thickness/4) * Box(rib_thickness, leg_length - 2*rib_width, thickness/2)
solid_body = solid_body + rib2

for x, y in [(leg_length/2 - hole_spacing/2, leg_width/2), (leg_length/2 + hole_spacing/2, leg_width/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

for x, y in [(leg_width/2, leg_length/2 - hole_spacing/2), (leg_width/2, leg_length/2 + hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

solid_body = solid_body - Pos(leg_width, leg_width, thickness/2) * Cylinder(pocket_radius, thickness)

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")