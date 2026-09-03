from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
thickness = 10.0
fillet_radius = 4.0
counterbore_diameter = 8.0
counterbore_depth = 3.0
through_hole_diameter = 5.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (leg_length_long,0), (leg_length_long,thickness),
                     (thickness,thickness), (thickness,leg_length_short),
                     (0,leg_length_short), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

cb_x = leg_length_long
cb_y = thickness / 2
cb_z = thickness / 2
solid_body = solid_body - Pos(cb_x - counterbore_depth/2, cb_y, cb_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(cb_x - leg_length_long/2, cb_y, cb_z) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, leg_length_long)

mh_x = mount_hole_offset
mh_y = thickness / 2
mh_z = thickness / 2
for i in range(2):
    hx = mh_x + (i - 0.5) * mount_hole_spacing
    solid_body = solid_body - Pos(hx, mh_y, mh_z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, thickness)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")