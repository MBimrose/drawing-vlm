from build123d import *

leg_length_x = 70.0
leg_length_y = 60.0
thickness = 8.0
depth = 12.0
inner_fillet_radius = 2.0
hole_diameter = 6.0
hole_offset = 30.0
gusset_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_x, 0), (leg_length_x, thickness),
                     (thickness, thickness), (thickness, leg_length_y),
                     (0, leg_length_y), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], inner_fillet_radius)

solid_body = solid_body - Pos(hole_offset, thickness / 2, 0) * Cylinder(hole_diameter / 2, depth * 2)
solid_body = solid_body - Pos(thickness / 2, hole_offset, 0) * Cylinder(hole_diameter / 2, depth * 2)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((0, 0), (gusset_thickness, 0), (0, gusset_thickness), close=True)
        make_face()
    extrude(amount=depth)

solid_body = solid_body + g.part

part = solid_body
part.name = "L_bracket_with_gusset"
export_step(part, "output.step")