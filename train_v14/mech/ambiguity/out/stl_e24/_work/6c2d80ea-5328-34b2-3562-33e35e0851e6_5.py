from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_thickness = 10.0
bracket_thickness = 8.0
rib_height = 4.0
rib_base = 12.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_end = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_thickness)
base = p.part

with BuildPart() as p2:
    with BuildSketch(Plane.XY.offset(bracket_thickness)) as sk2:
        with BuildLine() as bl2:
            Polyline((0,0), (rib_base, 0), (0, rib_base), close=True)
        make_face()
    extrude(amount=rib_height)
rib = p2.part

solid_body = base + rib

hole_positions = [
    (hole_offset_from_end, leg_thickness / 2),
    (hole_offset_from_end + hole_spacing, leg_thickness / 2),
    (hole_offset_from_end + 2 * hole_spacing, leg_thickness / 2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, bracket_thickness) * Cylinder(hole_diameter/2, bracket_thickness)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")