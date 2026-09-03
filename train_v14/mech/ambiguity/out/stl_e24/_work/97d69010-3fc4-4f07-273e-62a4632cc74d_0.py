from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
leg_thickness = 8.0
bracket_depth = 12.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
hole_spacing = 20.0
pocket_diameter = 20.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length + leg_thickness, leg_thickness),
                     (horizontal_leg_length + leg_thickness, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - leg_thickness) < 0.1 and abs(e.center().Y - leg_thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

for i in range(3):
    y = vertical_leg_length/2 + (i - 1) * hole_spacing
    solid_body = solid_body - Pos(leg_thickness/2, y, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

solid_body = solid_body - Pos(horizontal_leg_length/2 + leg_thickness/2, leg_thickness/2, bracket_depth) * Cylinder(pocket_diameter/2, pocket_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")