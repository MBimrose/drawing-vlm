from build123d import *
import math

body_length = 60.0
body_diameter = 40.0
flange_thickness = 10.0
flange_diameter = 60.0
bore_diameter = 30.0
wall_thickness = (body_diameter - bore_diameter) / 2.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = flange_diameter / 2.0 - 5.0
relief_groove_width = 8.0
relief_groove_depth = 3.0
relief_groove_position = body_length * 0.6
inlet_diameter = 6.0
inlet_offset = body_diameter / 2.0 - wall_thickness / 2.0 - 2.0
inlet_position = body_length * 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (body_diameter / 2.0, 0))
            l2 = Line(l1 @ 1, (body_diameter / 2.0, body_length))
            l3 = Line(l2 @ 1, (flange_diameter / 2.0, body_length))
            l4 = Line(l3 @ 1, (flange_diameter / 2.0, body_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, body_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
total_height = body_length + flange_thickness

solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(bore_diameter / 2.0, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(mount_hole_diameter / 2.0, total_height)

groove_z = relief_groove_position - relief_groove_width / 2.0
solid_body = solid_body - Pos(0, 0, groove_z) * Cylinder(bore_diameter / 2.0 - relief_groove_depth, relief_groove_width)

solid_body = solid_body - Pos(0, inlet_offset, inlet_position) * Rot(0, 90, 0) * Cylinder(inlet_diameter / 2.0, body_diameter)

part = solid_body
part.name = "revolved_body_with_flange"
export_step(part, "output.step")