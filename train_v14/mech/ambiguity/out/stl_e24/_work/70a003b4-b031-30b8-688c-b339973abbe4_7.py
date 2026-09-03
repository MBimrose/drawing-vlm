from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
slot_width = 4.0
slot_length = 12.0
slot_count = 4
slot_radius = (inner_diameter/2 + outer_diameter/2)/2
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

solid_body = Cylinder(outer_diameter/2, thickness)
solid_body = solid_body - Cylinder(inner_diameter/2, thickness)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Box(slot_length, slot_width, thickness)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "flanged_disk_with_slots"
export_step(part, "output.step")