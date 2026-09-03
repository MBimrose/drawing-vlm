from build123d import *

clip_length = 80.0
clip_width = 30.0
clip_thickness = 5.0
lobe_radius = 8.0
lobe_offset = 10.0
slot_width = 5.0
slot_length = 15.0
chamfer_dist = 1.0
mount_hole_dia = 4.0
mount_hole_spacing = 40.0
mount_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (clip_length, 0))
            l2 = Line(l1 @ 1, (clip_length, clip_width - lobe_radius))
            a1 = ThreePointArc(l2 @ 1, (clip_length - lobe_offset, clip_width), (clip_length - lobe_offset - lobe_radius, clip_width - lobe_radius))
            l3 = Line(a1 @ 1, (lobe_offset + lobe_radius, clip_width - lobe_radius))
            a2 = ThreePointArc(l3 @ 1, (lobe_offset, clip_width), (lobe_offset, clip_width - lobe_radius))
            l4 = Line(a2 @ 1, (0, clip_width - lobe_radius))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=clip_thickness)

solid_body = p.part
slot_cut = Pos(clip_length / 2, clip_width / 2, clip_thickness / 2) * Box(slot_width, slot_length, clip_thickness)
solid_body = solid_body - slot_cut

for x, y in [(clip_length / 2 - mount_hole_spacing / 2, clip_width / 2 - mount_hole_offset),
             (clip_length / 2 + mount_hole_spacing / 2, clip_width / 2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, clip_thickness / 2) * Cylinder(mount_hole_dia / 2, clip_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, chamfer_dist)

part = solid_body
part.name = "clip"
export_step(part, "output.step")