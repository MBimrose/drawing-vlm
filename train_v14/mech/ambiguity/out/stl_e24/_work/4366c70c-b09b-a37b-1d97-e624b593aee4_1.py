from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 20.0
thickness = 10.0
slot_width = 6.0
slot_length = 20.0
slot_center_radius = (inner_diameter/2 + outer_diameter/2) / 2
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0
mount_hole_count = 4

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_diameter/2, thickness * 2)

for i in range(4):
    angle = math.radians(i * 360.0 / 4)
    px = slot_center_radius * math.cos(angle)
    py = slot_center_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Box(slot_width, slot_length, thickness * 2)

for i in range(mount_hole_count):
    angle = math.radians(15 + i * 360.0 / mount_hole_count)
    px = mount_hole_offset * math.cos(angle)
    py = mount_hole_offset * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")