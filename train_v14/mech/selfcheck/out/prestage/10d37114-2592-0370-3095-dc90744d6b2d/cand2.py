from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
length = 60.0
shoulder_length = 15.0
shoulder_diameter = 50.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (shoulder_radius, length))
            l3 = Line(l2@1, (shoulder_radius, length - shoulder_length))
            l4 = Line(l3@1, (inner_radius, length - shoulder_length))
            l5 = Line(l4@1, (inner_radius, 0))
            l6 = Line(l5@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

hole_r = mount_hole_diameter / 2.0
for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, length / 2) * Cylinder(hole_r, length + 10)

part = solid_body
part.name = "revolved_cup_with_mount_holes"
export_step(part, "output.step")