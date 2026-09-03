from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
inner_fillet_radius = 15.0
outer_chamfer = 1.0
hole_diameter = 5.0
hole_spacing = 30.0
gusset_thickness = 4.0
gusset_length = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width), (leg_width, leg_width), (leg_width, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(leg_width/2, leg_width/2, thickness/2) * Cylinder(inner_fillet_radius, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), outer_chamfer)

for x, y in [(leg_length/2, leg_width/2), (leg_length/2 + hole_spacing, leg_width/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

for x, y in [(leg_width/2, leg_length/2), (leg_width/2, leg_length/2 + hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_length, 0), (0, gusset_length), close=True)
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")