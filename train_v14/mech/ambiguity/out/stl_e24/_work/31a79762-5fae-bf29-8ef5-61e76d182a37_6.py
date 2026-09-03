from build123d import *

plate_length = 100.0
plate_width = 30.0
plate_thickness = 5.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.1
hole_count = 6
hole_margin = 10.0
chamfer_distance = 2.0
rib_length = 20.0
rib_width = 5.0
rib_offset = 10.0

hole_spacing = (plate_length - 2 * hole_margin) / (hole_count - 1)
hole_positions = [(-plate_length/2 + hole_margin + i * hole_spacing, 0) for i in range(hole_count)]

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Box(slot_length, slot_width, plate_thickness)

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib_y = -plate_width/2 + rib_width/2
rib1 = Pos(-plate_length/2 + rib_offset, rib_y, 0) * Box(rib_length, rib_width, plate_thickness)
rib2 = Pos(plate_length/2 - rib_offset, rib_y, 0) * Box(rib_length, rib_width, plate_thickness)

part = solid_body + rib1 + rib2
part.name = "plate_with_slot_holes_ribs"
export_step(part, "output.step")