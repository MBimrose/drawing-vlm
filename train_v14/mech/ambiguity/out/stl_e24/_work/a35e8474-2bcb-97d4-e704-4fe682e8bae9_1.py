from build123d import *

leg_long = 80.0
leg_short = 70.0
thickness = 8.0
extrude_depth = 12.0
inner_fillet = 4.0
blind_hole_dia = 6.0
blind_hole_depth = 10.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_long, 0), (leg_long, thickness), (thickness, thickness), (thickness, leg_short), (0, leg_short), close=True)
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part

inner_edge = [e for e in solid_body.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1][0]
solid_body = fillet([inner_edge], inner_fillet)

solid_body = solid_body - Pos(thickness/2, leg_short/2, extrude_depth - blind_hole_depth/2) * Cylinder(blind_hole_dia/2, blind_hole_depth)

for x in [leg_long/2 - mount_hole_spacing/2, leg_long/2 + mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, thickness/2, extrude_depth/2) * Cylinder(mount_hole_dia/2, extrude_depth)

solid_body = solid_body - Pos(leg_long - pocket_width/2, thickness/2, pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")