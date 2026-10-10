from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
flange_thickness = 5.0
slot_width = 4.0
slot_length = 12.0
chamfer_angle_deg = 20.0
chamfer_distance = flange_thickness * math.tan(math.radians(chamfer_angle_deg))
mount_hole_dia = 5.0
mount_hole_offset = 25.0
clearance = 0.2

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, flange_thickness))
            l2 = Line(l1@1, (outer_radius, flange_thickness))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_center_x = outer_radius + slot_length / 2
slot = Pos(slot_center_x, 0, flange_thickness / 2) * Box(slot_length, slot_width, flange_thickness)
for angle in [0, 90, 180, 270]:
    solid_body = solid_body + Rot(0, angle, 0) * slot

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0), (0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, flange_thickness / 2) * Cylinder((mount_hole_dia + clearance) / 2, flange_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "flange_with_slots"
export_step(part, "output.step")