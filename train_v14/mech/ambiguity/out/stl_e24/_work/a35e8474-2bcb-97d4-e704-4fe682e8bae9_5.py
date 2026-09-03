from build123d import *

long_leg_length = 80.0
short_leg_length = 70.0
thickness = 8.0
depth = 12.0
inner_fillet_radius = 4.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 6.0
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (long_leg_length, 0), (long_leg_length, thickness),
                     (thickness, thickness), (thickness, short_leg_length),
                     (0, short_leg_length), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = [e for e in solid_body.edges().filter_by(Axis.Z)
               if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

pocket = Pos(long_leg_length - pocket_width/2, thickness/2, pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

blind_hole = Pos(thickness/2, short_leg_length/2, depth - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for x, y in [(long_leg_length/2 - mount_hole_spacing/2, thickness/2),
             (long_leg_length/2 + mount_hole_spacing/2, thickness/2)]:
    mount_hole = Pos(x, y, depth/2) * Cylinder(mount_hole_diameter/2, depth)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")