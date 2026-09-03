from build123d import *

base_width = 60.0
base_height = 20.0
arm_height = 50.0
arm_width = 30.0
thickness = 20.0
wall_thickness = 2.0
fillet_radius = 3.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-base_width/2, 0), (base_width/2, 0))
            l2 = Line(l1@1, (arm_width/2, arm_height))
            arc = ThreePointArc(l2@1, (0, arm_height + 20), (-arm_width/2, arm_height))
            l3 = Line(arc@1, (-base_width/2, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(-mount_hole_spacing/2, base_height/2), (mount_hole_spacing/2, base_height/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, thickness * 2)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

part = solid_body
part.name = "bracket"
export_step(part, "output.step")