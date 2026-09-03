from build123d import *

vertical_height = 70.0
horizontal_length = 80.0
thickness = 10.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 5.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, vertical_height))
            l2 = Line(l1 @ 1, (thickness, vertical_height))
            l3 = Line(l2 @ 1, (thickness, thickness))
            l4 = Line(l3 @ 1, (horizontal_length, thickness))
            l5 = Line(l4 @ 1, (horizontal_length, 0))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edge = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
solid_body = fillet([inner_edge], fillet_radius)

pocket = Pos(horizontal_length - pocket_width/2, thickness/2, thickness - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

cbore = Pos(thickness/2, vertical_height/2, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(thickness/2, vertical_height/2, thickness/2) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - thru

for x in [horizontal_length/2 - mount_hole_spacing/2, horizontal_length/2 + mount_hole_spacing/2]:
    hole = Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")