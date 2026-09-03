from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_width = 12.0
bracket_thickness = 8.0
inner_fillet_radius = 2.0
pocket_width = 6.0
pocket_length = 20.0
pocket_depth = 4.0
hole_diameter = 4.5
hole_spacing = 10.0
hole_offset_from_corner = 15.0
rib_width = 8.0
rib_height = 6.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_width),
                     (leg_length_long, leg_length_short + leg_width),
                     (leg_length_long - leg_width, leg_length_short + leg_width),
                     (leg_length_long - leg_width, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[1]
solid_body = fillet([inner_edge], inner_fillet_radius)

pocket_center_x = leg_length_long - leg_width / 2
pocket_center_y = leg_width + leg_length_short / 2
pocket = Pos(pocket_center_x, pocket_center_y, bracket_thickness - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

hole_center_x = leg_length_long - leg_width / 2
hole_center_y_base = leg_width + hole_offset_from_corner
for i in range(3):
    hy = hole_center_y_base + i * hole_spacing
    hole = Pos(hole_center_x, hy, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)
    solid_body = solid_body - hole

rib = Pos(leg_width / 2, leg_width / 2, bracket_thickness + rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")