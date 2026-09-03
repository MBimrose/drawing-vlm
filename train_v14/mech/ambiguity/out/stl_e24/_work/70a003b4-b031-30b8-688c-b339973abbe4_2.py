from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
chamfer_distance = 1.0
slot_width = 4.0
slot_length = 12.0
slot_count = 6
mount_hole_diameter = 5.0
mount_hole_offset = 30.0
central_pocket_diameter = 20.0
central_pocket_depth = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_radius = (outer_radius + inner_radius) / 2.0

solid_body = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(0, 0, thickness - central_pocket_depth/2) * Cylinder(central_pocket_diameter/2, central_pocket_depth)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Box(slot_width, slot_length, thickness)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness * 2)

part = solid_body
part.name = "ring_with_slots_and_mount_holes"
export_step(part, "output.step")