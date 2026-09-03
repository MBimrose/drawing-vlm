from build123d import *

horizontal_length = 70.0
vertical_length = 60.0
thickness = 8.0
depth = 12.0
fillet_radius = 4.0
hole_diameter = 6.0
hole_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_length, 0), (horizontal_length, thickness),
                     (thickness, thickness), (thickness, vertical_length),
                     (0, vertical_length), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], fillet_radius)

solid_body = solid_body - Pos(hole_offset, thickness/2, depth/2) * Cylinder(hole_diameter/2, depth)
solid_body = solid_body - Pos(thickness/2, hole_offset, depth/2) * Cylinder(hole_diameter/2, depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")