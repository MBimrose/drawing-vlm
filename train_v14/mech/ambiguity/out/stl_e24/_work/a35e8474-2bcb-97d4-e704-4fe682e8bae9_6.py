from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
thickness = 8.0
bracket_depth = 12.0
inner_fillet_radius = 3.0
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 6.0
pocket_depth = 6.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_leg_length))
            l2 = Line(l1@1, (thickness, vertical_leg_length))
            l3 = Line(l2@1, (thickness, thickness))
            l4 = Line(l3@1, (horizontal_leg_length, thickness))
            l5 = Line(l4@1, (horizontal_leg_length, 0))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], inner_fillet_radius)

solid_body = solid_body - Pos(thickness/2, vertical_leg_length/2, bracket_depth - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for x, y in [(horizontal_leg_length/2 - mount_hole_spacing/2, thickness/2),
             (horizontal_leg_length/2 + mount_hole_spacing/2, thickness/2)]:
    solid_body = solid_body - Pos(x, y, bracket_depth/2) * Cylinder(mount_hole_diameter/2, bracket_depth)

solid_body = solid_body - Pos(horizontal_leg_length - pocket_width/2, thickness/2, thickness/2) * Box(pocket_width, pocket_depth, pocket_height)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")