from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 70.0
leg_width = 30.0
thickness = 8.0
gusset_width = 30.0
gusset_height = 30.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 3.0
hole_spacing = 40.0
hole_offset_from_bottom = 20.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_width, 0), (leg_width, vertical_leg_length),
                     (leg_width + horizontal_leg_length, vertical_leg_length),
                     (leg_width + horizontal_leg_length, vertical_leg_length + leg_width),
                     (0, vertical_leg_length + leg_width), close=True)
        make_face()
    extrude(amount=thickness)
base = p.part

with BuildPart() as g:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (gusset_width, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=thickness)
gusset = g.part

solid_body = base + gusset

for x, y in [(leg_width/2, hole_offset_from_bottom), (leg_width/2, hole_offset_from_bottom + hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - Pos(x, y, thickness - cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - vertical_leg_length) < 1e-3]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")