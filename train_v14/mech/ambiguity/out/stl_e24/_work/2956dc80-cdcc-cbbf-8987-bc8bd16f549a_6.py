from build123d import *

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 5.0
slot_length = 30.0
slot_offset = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
chamfer_size = 0.5

solid_body = Cylinder(outer_diameter / 2, thickness)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness)

slot_x = outer_diameter / 2 - slot_offset - slot_length / 2
solid_body = solid_body - Pos(slot_x, 0, 0) * Box(slot_length, slot_width, thickness)
solid_body = solid_body - Pos(-slot_x, 0, 0) * Box(slot_length, slot_width, thickness)

solid_body = solid_body - Pos(0, mount_hole_spacing / 2, 0) * Cylinder(mount_hole_diameter / 2, thickness)
solid_body = solid_body - Pos(0, -mount_hole_spacing / 2, 0) * Cylinder(mount_hole_diameter / 2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")