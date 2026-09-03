from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 50.0
leg_thickness = 8.0
bracket_depth = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
pocket_width = 6.0
pocket_height = 30.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length + leg_thickness),
                     (0, vertical_leg_length + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_y = leg_thickness / 2
hole_x_start = leg_thickness + hole_offset_from_corner
for i in range(3):
    hx = hole_x_start + i * hole_spacing
    solid_body = solid_body - Pos(hx, hole_y, bracket_depth / 2) * Cylinder(hole_diameter / 2, bracket_depth)

pocket = Pos(leg_thickness / 2, vertical_leg_length + leg_thickness - pocket_depth / 2, bracket_depth) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")