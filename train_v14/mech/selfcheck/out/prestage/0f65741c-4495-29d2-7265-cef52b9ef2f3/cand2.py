from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 5.0
slot_width = 5.0
slot_height = 15.0
fillet_radius = 1.0
chamfer_distance = 1.0
mount_hole_dia = 4.0
mount_hole_spacing = 40.0
mount_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-jaw_length/2, -jaw_width/2), (jaw_length/2, -jaw_width/2))
            l2 = Line(l1@1, (jaw_length/2, jaw_width/2 - 10))
            a1 = ThreePointArc(l2@1, (jaw_length/2 - 5, jaw_width/2), (jaw_length/2 - 15, jaw_width/2 - 10))
            l3 = Line(a1@1, (-jaw_length/2 + 15, jaw_width/2 - 10))
            a2 = ThreePointArc(l3@1, (-jaw_length/2 + 5, jaw_width/2), (-jaw_length/2, jaw_width/2 - 10))
            l4 = Line(a2@1, (-jaw_length/2, -jaw_width/2))
        make_face()
    extrude(amount=jaw_thickness)

solid_body = p.part

slot = Box(slot_width, slot_height, jaw_thickness + 1)
solid_body = solid_body - slot

for x, y in [(-mount_hole_spacing/2, jaw_width/2 - mount_hole_offset),
             (mount_hole_spacing/2, jaw_width/2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, jaw_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

top_x_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[-2:]
solid_body = fillet(top_x_edges, fillet_radius)

part = solid_body
part.name = "jaw_with_slot_and_holes"
export_step(part, "output.step")