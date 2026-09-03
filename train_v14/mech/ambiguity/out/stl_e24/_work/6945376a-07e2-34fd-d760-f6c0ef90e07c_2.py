from build123d import *

horizontal_leg_length = 70.0
vertical_leg_length = 50.0
leg_width = 12.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = 4.5
hole_spacing = 10.0
hole_offset_from_top = 15.0
rib_width = 8.0
rib_height = 6.0
rib_thickness = 4.0
pocket_width = 6.0
pocket_length = 20.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, leg_width + vertical_leg_length),
                     (horizontal_leg_length + leg_width, leg_width + vertical_leg_length),
                     (horizontal_leg_length + leg_width, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z)
inner_edge = min(inner_edges, key=lambda e: (e.center().X - leg_width)**2 + (e.center().Y - leg_width)**2)
solid_body = fillet([inner_edge], fillet_radius)

hole_x = horizontal_leg_length + leg_width / 2
hole_y_start = leg_width + hole_offset_from_top
for i in range(3):
    hole_y = hole_y_start + i * hole_spacing
    solid_body = solid_body - Pos(hole_x, hole_y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

rib_center_x = leg_width / 2
rib_center_y = leg_width / 2
solid_body = solid_body + Pos(rib_center_x, rib_center_y, thickness + rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)

pocket_center_x = horizontal_leg_length + leg_width / 2
pocket_center_y = leg_width + vertical_leg_length / 2
solid_body = solid_body - Pos(pocket_center_x, pocket_center_y, thickness - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")