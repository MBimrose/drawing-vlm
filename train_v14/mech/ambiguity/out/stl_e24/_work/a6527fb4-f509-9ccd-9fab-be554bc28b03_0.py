from build123d import *

leg_thickness = 8.0
vertical_leg_length = 80.0
horizontal_leg_length = 60.0
bracket_width = 15.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
hole_edge_clearance = 4.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_width)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

pocket = Pos(leg_thickness/2, leg_thickness/2, bracket_width - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

hole_r = hole_diameter / 2
hole_h = bracket_width + 10
hole_z = bracket_width / 2

solid_body = solid_body - Pos(horizontal_leg_length - hole_edge_clearance, leg_thickness/2, hole_z) * Cylinder(hole_r, hole_h)

for i in range(3):
    y_pos = hole_edge_clearance + i * (vertical_leg_length - 2*hole_edge_clearance) / 2
    solid_body = solid_body - Pos(leg_thickness/2, y_pos, hole_z) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")