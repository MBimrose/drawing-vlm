from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
edge_fillet_radius = 1.0
chamfer_distance = 0.8
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 10.0
hole_count = 7
slot_width = 8.0
slot_length = plate_length - 20.0
slot_offset_y = -plate_width / 4.0
rib_width = 6.0
rib_height = 2.0
rib_spacing = 12.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_y_face.edges(), chamfer_distance)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 1)
solid_body = solid_body - Pos(0, slot_offset_y, 0) * slot_p.part

rib_count = int((plate_length - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    solid_body = solid_body + Pos(x, 0, rib_height / 2) * Box(rib_width, plate_width - 2 * rib_spacing, rib_height)

solid_body = solid_body - Pos(0, 0, -pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "plate_with_holes_slot_ribs_pocket"
export_step(part, "output.step")