from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
slot_length = 70.0
slot_width = 5.0
mount_hole_diameter = 4.0
mount_hole_radius = 35.0
mount_hole_count = 4
chamfer_distance = 1.0
fillet_radius = 0.5
rib_width = 5.0
rib_length = 30.0
rib_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_diameter / 2, thickness * 2)

with BuildPart() as sp:
    with BuildSketch() as ss:
        SlotOverall(slot_length, slot_width)
    extrude(amount=thickness * 2)
solid_body = solid_body - sp.part

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for i in range(mount_hole_count):
    angle = i * 90
    rib = Rot(0, 0, angle) * Pos(0, 0, thickness / 2 + rib_height / 2) * Box(rib_width, rib_length, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "flanged_disc_with_ribs"
export_step(part, "output.step")