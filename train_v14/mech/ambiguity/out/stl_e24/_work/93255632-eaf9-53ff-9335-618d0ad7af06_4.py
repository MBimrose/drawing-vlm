from build123d import *

overall_width = 80.0
overall_length = 60.0
overall_height = 12.0
wall_thickness = 5.0
arch_height = 12.0
keyway_width = 6.0
keyway_depth = 8.0
keyway_length = 30.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-overall_width/2, -overall_length/2), (overall_width/2, -overall_length/2))
            l2 = Line(l1@1, (overall_width/2, overall_length/2))
            a1 = ThreePointArc(l2@1, (0, overall_length/2 + arch_height), (-overall_width/2, overall_length/2))
            l3 = Line(a1@1, l1@0)
        make_face()
    extrude(amount=overall_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

keyway = Pos(0, 0, overall_height/2 - keyway_depth/2) * Box(keyway_width, keyway_length, keyway_depth)
solid_body = solid_body - keyway

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, overall_height + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "arched_bracket"
export_step(part, "output.step")