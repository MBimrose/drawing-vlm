from build123d import *

vertical_leg_height = 80.0
horizontal_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 15.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_height), (leg_thickness, vertical_leg_height),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(leg_thickness/2, vertical_leg_height/2, bracket_depth/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(horizontal_leg_length - pocket_width/2, leg_thickness/2, bracket_depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

hole_r = hole_diameter / 2
hole_h = bracket_depth + 10
for y in [vertical_leg_height/3, 2*vertical_leg_height/3]:
    solid_body = solid_body - Pos(leg_thickness/2, y, bracket_depth/2) * Cylinder(hole_r, hole_h)
solid_body = solid_body - Pos(horizontal_leg_length - leg_thickness/2, leg_thickness/2, bracket_depth/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")