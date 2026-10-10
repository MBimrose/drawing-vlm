from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 10.0
bracket_thickness = 8.0
rib_height = 4.0
rib_width = 12.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_corner = 20.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part

with BuildPart() as rib_p:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_bl:
            Polyline((0, 0), (rib_width, 0), (0, rib_width), close=True)
        make_face()
    extrude(amount=rib_height)

rib = Pos(leg_thickness, leg_thickness, bracket_thickness) * rib_p.part
solid_body = solid_body + rib

for i in range(3):
    x = hole_offset_from_corner + i * hole_spacing
    y = leg_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness) * Cylinder(hole_diameter / 2, bracket_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")