from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 8.0
central_hole_diameter = 20.0
countersink_diameter = 30.0
countersink_depth = 3.0
slot_length = 20.0
slot_width = 8.0
slot_offset = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 24.0
rib_width = 6.0
rib_height = 4.0
rib_offset = 12.0
chamfer_distance = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - countersink_depth/2) * Cylinder(countersink_diameter/2, countersink_depth)

slot_center_x = plate_length/2 - slot_offset - slot_length/2
slot_box = Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Pos(slot_center_x, 0, 0) * slot_box
solid_body = solid_body - Pos(-slot_center_x, 0, 0) * slot_box

mount_hole = Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, plate_length)
solid_body = solid_body - Pos(0, mount_hole_spacing/2, 0) * mount_hole
solid_body = solid_body - Pos(0, -mount_hole_spacing/2, 0) * mount_hole

rib = Box(rib_width, plate_width - 2*slot_offset, rib_height)
rib_center_x = plate_length/2 - rib_offset - rib_width/2
solid_body = solid_body + Pos(rib_center_x, 0, plate_thickness + rib_height/2) * rib
solid_body = solid_body + Pos(-rib_center_x, 0, plate_thickness + rib_height/2) * rib

part = solid_body
part.name = "plate_with_holes_slots_and_ribs"
export_step(part, "output.step")