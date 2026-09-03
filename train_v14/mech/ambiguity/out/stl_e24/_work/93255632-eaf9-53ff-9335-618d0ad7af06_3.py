from build123d import *

outer_width = 80.0
outer_height = 60.0
outer_thickness = 12.0
wall_thickness = 5.0
keyway_width = 6.0
keyway_depth = 30.0
keyway_cut_depth = 3.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-outer_width/2, -outer_height/2), (outer_width/2, -outer_height/2))
            l2 = Line(l1@1, (outer_width/2, outer_height/2 - 10))
            arc = ThreePointArc(l2@1, (0, outer_height/2 + 12), (-outer_width/2, outer_height/2 - 10))
            l3 = Line(arc@1, (-outer_width/2, -outer_height/2))
        make_face()
    extrude(amount=outer_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

keyway = Pos(0, 0, keyway_cut_depth/2) * Box(keyway_width, keyway_depth, keyway_cut_depth)
solid_body = solid_body - keyway

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, outer_thickness/2) * Cylinder(mount_hole_dia/2, outer_thickness + 1)
    solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_keyway_and_holes"
export_step(part, "output.step")