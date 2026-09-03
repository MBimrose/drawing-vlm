from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 60.0
thickness = 6.0
bracket_depth = 30.0
inner_fillet_radius = 10.0
hole_diameter = 8.0
hole_offset = 12.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid = p.part
inner_edges = [e for e in solid.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid = fillet(inner_edges, inner_fillet_radius)

hole_r = hole_diameter / 2
hole_h = bracket_depth
solid = solid - Pos(horizontal_leg_length - hole_offset - hole_diameter/2, thickness/2, 0) * Cylinder(hole_r, hole_h)
solid = solid - Pos(thickness/2, vertical_leg_length - hole_offset - hole_diameter/2, 0) * Cylinder(hole_r, hole_h)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")