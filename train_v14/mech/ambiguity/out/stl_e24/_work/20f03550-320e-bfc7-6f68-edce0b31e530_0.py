from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 50.0
leg_thickness = 8.0
bracket_width = 12.0
pocket_width = 6.0
pocket_height = 10.0
pocket_depth = 5.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_length + leg_thickness),
                     (0, vertical_leg_length + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_width)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(leg_thickness/2, vertical_leg_length + leg_thickness - pocket_depth/2, bracket_width) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_width/2) * Cylinder(hole_diameter/2, bracket_width)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")