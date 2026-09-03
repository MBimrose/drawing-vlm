from build123d import *

outer_diameter = 50.0
inner_diameter = 21.0
thickness = 10.0
slot_width = 5.0
slot_depth = 8.0
chamfer_size = 0.8
mount_hole_diameter = 4.5
mount_hole_spacing = 30.0

solid_body = Cylinder(outer_diameter / 2, thickness)
solid_body = solid_body - Cylinder(inner_diameter / 2, thickness)

slot_center_x = inner_diameter / 2 + slot_depth / 2
slot = Pos(slot_center_x, 0, 0) * Box(slot_width, slot_depth, thickness)
solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for x, y in [(-mount_hole_spacing / 2, 0), (mount_hole_spacing / 2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, thickness)

part = solid_body
part.name = "flanged_disc_with_slot"
export_step(part, "output.step")