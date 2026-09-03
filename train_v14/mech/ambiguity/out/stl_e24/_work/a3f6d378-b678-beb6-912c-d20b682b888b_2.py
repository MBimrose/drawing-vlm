from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
slot_length = 70.0
slot_width = 6.0
slot_offset_from_edge = 10.0
hole_diameter = 6.0
hole_spacing = 10.0
hole_count = 7
chamfer_size = 0.8
fillet_radius = 1.0
rib_height = 2.0
rib_width = 10.0
rib_length = 30.0

solid_body = Box(plate_length, plate_width, plate_thickness)

slot_center_x = -plate_length/2 + slot_offset_from_edge + slot_length/2
slot_center_y = -plate_width/2 + slot_offset_from_edge + slot_width/2

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = Pos(slot_center_x, slot_center_y, -plate_thickness) * slot_bp.part
solid_body = solid_body - slot_solid

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 2)

top_face = solid_body.faces().sort_by(Axis.Y)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

rib = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_holes_rib"
export_step(part, "output.step")