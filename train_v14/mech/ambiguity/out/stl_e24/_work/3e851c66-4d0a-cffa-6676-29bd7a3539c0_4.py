from build123d import *

horizontal_length = 80.0
vertical_length = 60.0
thickness = 6.0
bracket_depth = 30.0
inner_fillet_radius = 10.0
hole_diameter = 8.0
hole_offset = 30.0
gusset = True

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_length), (0, vertical_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 1e-3 and abs(e.center().Y - thickness) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

solid_body = solid_body - Pos(horizontal_length - hole_offset, thickness / 2, 0) * Cylinder(hole_diameter / 2, bracket_depth)
solid_body = solid_body - Pos(thickness / 2, vertical_length - hole_offset, 0) * Cylinder(hole_diameter / 2, bracket_depth)

if gusset:
    with BuildPart() as gp:
        with BuildSketch() as gsk:
            with BuildLine() as gbl:
                Polyline((0, 0), (thickness, 0), (0, thickness), close=True)
            make_face()
        extrude(amount=bracket_depth)
    solid_body = solid_body + gp.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")