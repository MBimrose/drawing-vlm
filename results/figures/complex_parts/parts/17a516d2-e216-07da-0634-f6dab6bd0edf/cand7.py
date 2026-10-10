from build123d import *

leg_length = 70.0
leg_height = 60.0
thickness = 8.0
depth = 12.0
inner_chamfer = 2.0
hole_diameter = 6.0
gusset_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length + thickness, 0), (leg_length + thickness, thickness),
                     (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = chamfer(inner_edges, inner_chamfer)

solid_body = solid_body - Pos(leg_length / 2, thickness / 2, depth / 2) * Cylinder(hole_diameter / 2, depth)
solid_body = solid_body - Pos(thickness / 2, leg_height / 2, depth / 2) * Cylinder(hole_diameter / 2, depth)

with BuildPart() as g:
    with BuildSketch() as gs:
        with BuildLine() as gl:
            Polyline((0, 0), (gusset_thickness, 0), (0, gusset_thickness), close=True)
        make_face()
    extrude(amount=depth)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")