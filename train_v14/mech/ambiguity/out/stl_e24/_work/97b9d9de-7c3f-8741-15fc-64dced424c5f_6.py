from build123d import *

vertical_leg_length = 70.0
horizontal_leg_length = 80.0
thickness = 10.0
rib_width = 10.0
rib_height = 5.0
rib_offset = 5.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
through_hole_diameter = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_offset = 5.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (thickness, vertical_leg_length),
                     (thickness, thickness), (horizontal_leg_length, thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

rib = Pos(thickness/2, vertical_leg_length - rib_offset - rib_width/2, rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

cbore = Pos(thickness/2, vertical_leg_length/2, thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(thickness/2, vertical_leg_length/2, thickness/2) * Cylinder(through_hole_diameter/2, thickness)
solid_body = solid_body - thru

for x, y in [(mount_hole_offset, 0), (mount_hole_offset + mount_hole_spacing, 0)]:
    hole = Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - hole

pocket = Pos(horizontal_leg_length - pocket_offset - pocket_width/2, thickness/2, thickness - thickness/4) * Box(pocket_width, pocket_depth, thickness/2)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")