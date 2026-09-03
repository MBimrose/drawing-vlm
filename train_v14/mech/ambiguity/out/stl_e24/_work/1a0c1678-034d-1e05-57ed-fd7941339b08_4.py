from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 50.0
bracket_thickness = 8.0
rib_width = 6.0
rib_height = 20.0
rib_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, bracket_thickness),
                     (bracket_thickness, bracket_thickness), (bracket_thickness, vertical_leg_length),
                     (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(bracket_thickness/2, bracket_thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for i in range(4):
    x = hole_offset_from_end + i * hole_spacing
    y = bracket_thickness / 2
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness)

for i in range(2):
    y = mount_hole_offset + i * mount_hole_spacing
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, horizontal_leg_length)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")