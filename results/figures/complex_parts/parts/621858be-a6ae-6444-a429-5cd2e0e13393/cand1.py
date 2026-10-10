from build123d import *
import math

outer_radius = 45.0
inner_radius = 40.0
ring_height = 30.0
lip_height = 5.0
lip_thickness = 3.0
slot_width = 8.0
slot_depth = 15.0
slot_count = 6
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, ring_height - lip_height))
            l2 = Line(l1@1, (outer_radius, ring_height - lip_height))
            l3 = Line(l2@1, (outer_radius + lip_thickness, ring_height - lip_height))
            l4 = Line(l3@1, (outer_radius + lip_thickness, ring_height))
            l5 = Line(l4@1, (outer_radius, ring_height))
            l6 = Line(l5@1, (outer_radius, 0))
            l7 = Line(l6@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_width, slot_depth, ring_height)
    solid_body = solid_body - slot

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, ring_height / 2) * Cylinder(mount_hole_dia / 2, ring_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "ring_with_slots_and_mount_holes"
export_step(part, "output.step")