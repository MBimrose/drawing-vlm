from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 5.0
corner_fillet_radius = 3.0
hole_diameter = 11.0
hole_spacing = 12.0
hole_count = 5
hole_depth = 4.0
slot_width = 10.0
slot_length = 20.0
slot_offset_from_left = 5.0
rib_height = 2.0
rib_thickness = 2.0
rib_length = plate_length - 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

slot_center_x = -plate_length/2 + slot_offset_from_left + slot_length/2
slot_cut = Pos(slot_center_x, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot_cut

hole_start_x = -plate_length/2 + 30.0
for i in range(hole_count):
    hx = hole_start_x + i * hole_spacing
    hole_cut = Pos(hx, 0, plate_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole_cut

rib = Pos(0, 0, rib_height/2) * Box(rib_length, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")