from build123d import *

vertical_leg_length = 60.0
horizontal_leg_length = 70.0
leg_width = 30.0
thickness = 8.0
inner_fillet_radius = 5.0
hole_clearance_diameter = 6.0
hole_cbore_diameter = 10.0
hole_cbore_depth = 3.0
hole_spacing = 40.0
hole_offset_from_bottom = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, vertical_leg_length),
                     (leg_width + horizontal_leg_length, vertical_leg_length),
                     (leg_width + horizontal_leg_length, vertical_leg_length + leg_width),
                     (0, vertical_leg_length + leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - vertical_leg_length) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

for x, y in [(leg_width/2, hole_offset_from_bottom), (leg_width/2, hole_offset_from_bottom + hole_spacing)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_clearance_diameter/2, thickness)
    solid_body = solid_body - Pos(x, y, thickness - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")