from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
slot_length = 30.0
slot_width = 12.0
hole_diameter = 8.0
hole_offset_x = 20.0
chamfer_distance = 1.0
rib_height = 3.0
rib_width = 10.0
rib_spacing = 15.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = chamfer(solid_body.edges(), chamfer_distance)

slot_cut = Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - slot_cut

hole_cut = Cylinder(hole_diameter / 2, plate_thickness * 2)
solid_body = solid_body - Pos(-hole_offset_x, 0, 0) * hole_cut
solid_body = solid_body - Pos(hole_offset_x, 0, 0) * hole_cut

rib_count = int((plate_length - 2 * rib_spacing) // rib_spacing) + 1
rib_positions = [(-plate_length/2 + rib_spacing + i * rib_spacing) for i in range(rib_count)]

rib = Box(rib_width, rib_height, plate_thickness / 2)
for x in rib_positions:
    solid_body = solid_body + Pos(x, 0, -plate_thickness/4) * rib

part = solid_body
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")