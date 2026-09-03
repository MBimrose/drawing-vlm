from build123d import *

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 20.0
slot_width = 5.0
slot_length = outer_diameter
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
boss_diameter = 12.0
boss_height = 2.0

solid_body = Cylinder(outer_diameter / 2, thickness)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness)
solid_body = solid_body - Box(slot_length, slot_width, thickness)

for y in [mount_hole_spacing / 2, -mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(0, y, 0) * Cylinder(mount_hole_diameter / 2, thickness)

solid_body = solid_body + Pos(0, 0, thickness / 2 - boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "flanged_disc_with_slot"
export_step(part, "output.step")