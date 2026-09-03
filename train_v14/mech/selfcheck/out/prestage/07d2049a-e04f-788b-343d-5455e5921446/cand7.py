from build123d import *
import math

hub_diameter = 30.0
hub_length = 20.0
head_diameter = 80.0
head_length = 25.0
bore_diameter = 12.0
fillet_radius = 3.0
chamfer_distance = 2.0
mount_hole_diameter = 5.0
mount_hole_offset_angle = 45.0
mount_hole_radius = (head_diameter/2) - 10.0

hub_radius = hub_diameter/2
head_radius = head_diameter/2
bore_radius = bore_diameter/2
total_length = hub_length + head_length

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (hub_radius, 0))
            l2 = Line(l1@1, (hub_radius, hub_length))
            l3 = Line(l2@1, (head_radius, hub_length))
            l4 = Line(l3@1, (head_radius, total_length))
            l5 = Line(l4@1, (0, total_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, total_length/2) * Cylinder(bore_radius, total_length)

for i in range(2):
    angle = math.radians(mount_hole_offset_angle + i * 180.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_length/2) * Cylinder(mount_hole_diameter/2, total_length)

part = solid_body
part.name = "hub_with_head"
export_step(part, "output.step")