from build123d import *

outer_diameter = 80.0
flange_thickness = 5.0
shoulder1_diameter = 45.7
shoulder1_length = 15.0
shoulder2_diameter = 31.4
shoulder2_length = 10.0
shaft_diameter = 14.3
shaft_length = 40.0
keyway_width = 6.0
keyway_depth = 4.0
chamfer_size = 0.5
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

outer_radius = outer_diameter / 2.0
shoulder1_radius = shoulder1_diameter / 2.0
shoulder2_radius = shoulder2_diameter / 2.0
shaft_radius = shaft_diameter / 2.0
total_length = flange_thickness + shoulder1_length + shoulder2_length + shaft_length

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, flange_thickness))
            l3 = Line(l2 @ 1, (shoulder1_radius, flange_thickness))
            l4 = Line(l3 @ 1, (shoulder1_radius, flange_thickness + shoulder1_length))
            l5 = Line(l4 @ 1, (shoulder2_radius, flange_thickness + shoulder1_length))
            l6 = Line(l5 @ 1, (shoulder2_radius, flange_thickness + shoulder1_length + shoulder2_length))
            l7 = Line(l6 @ 1, (shaft_radius, flange_thickness + shoulder1_length + shoulder2_length))
            l8 = Line(l7 @ 1, (shaft_radius, total_length))
            l9 = Line(l8 @ 1, (0, total_length))
            l10 = Line(l9 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Y)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

keyway_box = Pos(0, total_length / 2, 0) * Box(keyway_width, total_length, keyway_depth)
solid_body = solid_body - keyway_box

for x, z in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    hole = Pos(x, total_length / 2, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, total_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")