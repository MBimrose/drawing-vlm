from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 8.0
bracket_depth = 15.0
inner_fillet_radius = 4.0
hole_diameter = 6.0
hole_count_vertical = 3
hole_count_horizontal = 1
rib_width = 5.0
rib_height = 10.0
rib_thickness = 3.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - leg_thickness) < 1e-3 and abs(e.center().Y - leg_thickness) < 1e-3]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(leg_thickness/2, leg_thickness/2, bracket_depth/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

pocket = Pos(horizontal_leg_length - pocket_width/2, leg_thickness/2, bracket_depth - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_count_vertical):
    y = vertical_leg_length / (hole_count_vertical + 1) * (i + 1)
    solid_body = solid_body - Pos(leg_thickness/2, y, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

for i in range(hole_count_horizontal):
    x = horizontal_leg_length - (horizontal_leg_length - leg_thickness) / 2
    solid_body = solid_body - Pos(x, leg_thickness/2, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")