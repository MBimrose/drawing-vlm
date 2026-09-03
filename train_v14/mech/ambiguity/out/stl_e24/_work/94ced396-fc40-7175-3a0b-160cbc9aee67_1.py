from build123d import *

long_leg_length = 80.0
short_leg_length = 60.0
leg_width = 20.0
thickness = 5.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (short_leg_length, 0), (short_leg_length, leg_width),
                     (short_leg_length, leg_width + long_leg_length),
                     (short_leg_length - leg_width, leg_width + long_leg_length),
                     (short_leg_length - leg_width, leg_width), (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body + Pos(short_leg_length - leg_width/2, leg_width + long_leg_length, thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body - Pos(short_leg_length - leg_width/2, leg_width + long_leg_length, thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(short_leg_length - leg_width/2, leg_width + long_leg_length, (thickness + boss_height)/2) * Cylinder(boss_hole_diameter/2, thickness + boss_height + 20)
for x, y in [(short_leg_length/2 - mount_hole_spacing/2, leg_width/2),
             (short_leg_length/2 + mount_hole_spacing/2, leg_width/2)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness + 10)
chamfer_edges = solid_body.edges().filter_by(Axis.Y).sort_by(Axis.X)[:2]
solid_body = chamfer(chamfer_edges, chamfer_size)
part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")