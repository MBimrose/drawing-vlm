from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 6.0
slot_length = 70.0
slot_width = 8.0
slot_offset_y = -10.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 10.0
hole_count = 7
chamfer_size = 0.8
fillet_radius = 1.0
rib_width = 12.0
rib_height = 8.0
rib_thickness = 2.0
rib_offset_x = -30.0
rib_offset_y = -15.0
pocket_diameter = 20.0
pocket_depth = 2.0
pocket_offset_x = -15.0
pocket_offset_y = 0.0

solid_body = Box(plate_width, plate_height, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2, both=True)
slot_solid = Pos(0, slot_offset_y, 0) * slot_bp.part
solid_body = solid_body - slot_solid

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

solid_body = solid_body - Pos(pocket_offset_x, pocket_offset_y, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

solid_body = solid_body + Pos(rib_offset_x, rib_offset_y, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(front_face.edges(), chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_slot_holes_pocket_rib"
export_step(part, "output.step")