from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 55.0
leg_width = 12.0
thickness = 10.0
inner_fillet_radius = 2.0
hole_diameter = 5.0
hole_offset_along_leg = 30.0
gusset_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_leg_length, 0))
            l2 = Line(l1 @ 1, (horizontal_leg_length, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, vertical_leg_length))
            l5 = Line(l4 @ 1, (0, vertical_leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_width) < 1e-3 and abs(e.center().Y - leg_width) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(hole_offset_along_leg, leg_width / 2, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - Pos(leg_width / 2, vertical_leg_length - hole_offset_along_leg, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            gl1 = Line((0, 0), (leg_width, 0))
            gl2 = Line(gl1 @ 1, (0, leg_width))
            gl3 = Line(gl2 @ 1, (0, 0))
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")