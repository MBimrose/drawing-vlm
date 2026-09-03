from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
bracket_thickness = 8.0
bracket_depth = 15.0
inner_fillet_radius = 3.0
hole_diameter = 6.0
hole_edge_offset = 4.0
gusset_thickness = 4.0
gusset_leg_length = 10.0
pocket_width = 12.0
pocket_depth = 8.0
pocket_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (bracket_thickness, vertical_leg_length),
                     (bracket_thickness, bracket_thickness), (horizontal_leg_length, bracket_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - bracket_thickness) < 0.1 and abs(e.center().Y - bracket_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_r = hole_diameter / 2
hole_h = bracket_depth + 1
for y in [vertical_leg_length/3, 2*vertical_leg_length/3]:
    solid_body = solid_body - Pos(bracket_thickness/2, y, bracket_depth/2) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(horizontal_leg_length - hole_edge_offset, bracket_thickness/2, bracket_depth/2) * Cylinder(hole_r, hole_h)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            Polyline((bracket_thickness, bracket_thickness),
                     (bracket_thickness + gusset_leg_length, bracket_thickness),
                     (bracket_thickness, bracket_thickness + gusset_leg_length), close=True)
        make_face()
    extrude(amount=bracket_depth)
solid_body = solid_body + g.part

pocket_x = horizontal_leg_length - pocket_offset
solid_body = solid_body - Pos(pocket_x, bracket_thickness/2, bracket_depth - pocket_depth/4) * Box(pocket_width, pocket_depth, pocket_depth/2)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")