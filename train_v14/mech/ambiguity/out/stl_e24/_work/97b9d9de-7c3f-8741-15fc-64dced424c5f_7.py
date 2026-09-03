from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
thickness = 10.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 5.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

pocket = Pos(horizontal_leg_length - pocket_width/2, thickness/2, thickness - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

cbore = Pos(thickness/2, vertical_leg_length/2, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(thickness/2, vertical_leg_length/2, thickness/2) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - thru

for x in [horizontal_leg_length/2 - mount_hole_spacing/2, horizontal_leg_length/2 + mount_hole_spacing/2]:
    hole = Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")