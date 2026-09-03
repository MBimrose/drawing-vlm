from build123d import *

clip_length = 80.0
clip_width = 12.0
clip_thickness = 6.0
nose_length = 20.0
nose_radius = 6.0
slot_width = 4.0
slot_length = 30.0
slot_offset = 10.0
rib_width = 3.0
rib_height = 2.0
rib_spacing = 15.0
pocket_width = 6.0
pocket_depth = 3.0
pocket_offset = 20.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (clip_length, 0), (clip_length, clip_width - slot_width),
                     (slot_offset + slot_length, clip_width - slot_width),
                     (slot_offset + slot_length, clip_width),
                     (slot_offset, clip_width), (0, clip_width), close=True)
        make_face()
    extrude(amount=clip_thickness)

solid_body = p.part
solid_body = solid_body + Pos(clip_length, clip_width / 2, 0) * Rot(0, 90, 0) * Cylinder(nose_radius, nose_length)

slot_center_x = slot_offset + slot_length / 2
solid_body = solid_body - Pos(slot_center_x, clip_width - clip_thickness / 2, clip_thickness / 2) * Box(slot_width, clip_thickness, slot_length)

rib_count = int((clip_length - 2 * rib_spacing) // rib_spacing) + 1
rib_positions = [rib_spacing + i * rib_spacing for i in range(rib_count)]
for x in rib_positions:
    solid_body = solid_body - Pos(x, clip_width / 2, clip_thickness / 4) * Box(rib_width, rib_height, clip_thickness / 2)

pocket_center_x = pocket_offset + pocket_width / 2
solid_body = solid_body - Pos(pocket_center_x, clip_width - pocket_depth / 2, clip_thickness / 2) * Box(pocket_width, pocket_depth, pocket_depth)

part = solid_body
part.name = "clip"
export_step(part, "output.step")