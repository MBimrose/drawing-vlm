from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
edge_fillet_radius = 1.0
chamfer_distance = 0.8
hole_diameter = 6.0
hole_spacing = 10.0
hole_count = 7
slot_length = plate_width * 0.8
slot_width = 6.0
slot_offset_y = -plate_height * 0.25
rib_width = 20.0
rib_height = 10.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness) * Cylinder(hole_diameter / 2, plate_thickness + 2)

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 2)
solid_body = solid_body - Pos(0, slot_offset_y, 0) * slot_p.part

rib = Pos(0, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_holes_slot_and_rib"
export_step(part, "output.step")