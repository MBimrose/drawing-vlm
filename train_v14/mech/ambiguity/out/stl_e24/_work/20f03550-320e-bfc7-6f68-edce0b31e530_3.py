from build123d import *

horizontal_leg_length = 70.0
vertical_leg_height = 50.0
leg_thickness = 8.0
bracket_depth = 12.0
rib_width = 6.0
rib_height = 30.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset_from_corner = 15.0
fillet_radius = 2.0
pocket_width = 10.0
pocket_height = 20.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, vertical_leg_height + leg_thickness),
                     (0, vertical_leg_height + leg_thickness), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(leg_thickness/2, vertical_leg_height/2 + leg_thickness, bracket_depth/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for i in range(3):
    hx = hole_offset_from_corner + i * hole_spacing
    hy = leg_thickness / 2
    solid_body = solid_body - Pos(hx, hy, bracket_depth/2) * Cylinder(hole_diameter/2, bracket_depth + 10)

pocket = Pos(leg_thickness/2, vertical_leg_height + leg_thickness - pocket_depth/2, bracket_depth/2 + vertical_leg_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")