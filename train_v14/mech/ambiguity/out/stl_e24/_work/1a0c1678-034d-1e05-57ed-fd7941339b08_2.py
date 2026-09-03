from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_thickness = 8.0
bracket_depth = 8.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
mount_hole_diameter = 6.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0
rib_width = 6.0
rib_height = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_thickness),
                     (leg_thickness, leg_thickness), (leg_thickness, leg_length_short),
                     (0, leg_length_short), close=True)
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole_positions = [hole_offset_from_end + i * hole_spacing for i in range(4)]
for x in hole_positions:
    solid_body = solid_body - Pos(x, leg_thickness / 2, 0) * Cylinder(hole_diameter / 2, bracket_depth * 2)

mount_positions = [mount_hole_offset + i * mount_hole_spacing for i in range(2)]
for y in mount_positions:
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, leg_length_long * 2)

rib = Pos(leg_thickness / 2, leg_thickness / 2, bracket_depth / 2) * Box(rib_width, rib_height, bracket_depth)
solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")