from build123d import *

horizontal_length = 80.0
vertical_length = 70.0
thickness = 10.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 6.0
rib_thickness = 4.0
screw_hole_diameter = 4.0
screw_head_diameter = 8.0
screw_head_depth = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (horizontal_length, 0))
            l2 = Line(l1@1, (horizontal_length, thickness))
            l3 = Line(l2@1, (thickness, thickness))
            l4 = Line(l3@1, (thickness, vertical_length))
            l5 = Line(l4@1, (0, vertical_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

rib = Pos(thickness/2, thickness/2, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

cbore = Pos(thickness/2, vertical_length/2, thickness - screw_head_depth/2) * Cylinder(screw_head_diameter/2, screw_head_depth)
shaft = Pos(thickness/2, vertical_length/2, thickness/2) * Cylinder(screw_hole_diameter/2, thickness)
solid_body = solid_body - cbore - shaft

for x in [horizontal_length/2 - mount_hole_spacing/2, horizontal_length/2 + mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

pocket = Pos(horizontal_length - pocket_width/2 - 5, thickness/2, thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")