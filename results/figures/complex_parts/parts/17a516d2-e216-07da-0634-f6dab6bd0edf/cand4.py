from build123d import *

leg_length = 70.0
leg_height = 60.0
thickness = 8.0
bracket_thickness = 12.0
inner_fillet_radius = 2.0
hole_diameter = 6.0
hole_offset_along_leg = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length + thickness, 0), (leg_length + thickness, thickness),
                     (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_r = hole_diameter / 2
hole_h = bracket_thickness + 2
solid_body = solid_body - Pos(thickness + hole_offset_along_leg, thickness / 2, bracket_thickness / 2) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(thickness / 2, leg_height - hole_offset_along_leg, bracket_thickness / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")