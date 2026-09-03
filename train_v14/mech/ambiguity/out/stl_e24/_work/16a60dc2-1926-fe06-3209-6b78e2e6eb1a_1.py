from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 12.0
thickness = 15.0
blind_hole_depth = 10.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
slot_width = 3.0
slot_depth = 5.0
slot_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, thickness - blind_hole_depth/2) * Cylinder(inner_radius, blind_hole_depth)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, thickness/2) * Box(slot_width, slot_depth, thickness)
    solid_body = solid_body - slot

part = solid_body
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")