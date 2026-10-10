from build123d import *

leg_length = 60.0
leg_height = 80.0
leg_thickness = 10.0
bracket_thickness = 8.0
gusset_size = 12.0
hole_diameter = 4.0
hole_depth = 4.0
hole_spacing = 15.0
hole_offset = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_height),
                     (0, leg_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_size, 0), (0, gusset_size), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = solid_body + g.part

for i in range(3):
    x = hole_offset + i * hole_spacing
    y = leg_thickness / 2
    z = bracket_thickness - hole_depth / 2
    solid_body = solid_body - Pos(x, y, z) * Cylinder(hole_diameter / 2, hole_depth)

chamfer_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-1:]
solid_body = chamfer(chamfer_edges, chamfer_size)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")