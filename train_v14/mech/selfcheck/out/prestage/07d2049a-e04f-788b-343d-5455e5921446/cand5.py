from build123d import *
import math

outer_diameter = 80.0
flange_thickness = 25.0
hub_diameter = 30.0
hub_length = 20.0
bore_diameter = 12.0
fillet_radius = 3.0
keyway_width = 8.0
keyway_depth = 6.0
mount_hole_diameter = 5.0
mount_hole_offset_angle = 45.0
mount_hole_radius = (outer_diameter / 2) - 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (hub_diameter / 2, 0))
            l2 = Line(l1 @ 1, (hub_diameter / 2, hub_length))
            l3 = Line(l2 @ 1, (outer_diameter / 2, hub_length))
            l4 = Line(l3 @ 1, (outer_diameter / 2, hub_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, hub_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

total_height = hub_length + flange_thickness
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(bore_diameter / 2, total_height + 10)

keyway_box = Pos(hub_diameter / 2 - keyway_depth / 2, 0, hub_length / 2) * Box(keyway_depth, keyway_width, hub_length)
solid_body = solid_body - keyway_box

for i in range(2):
    angle = math.radians(mount_hole_offset_angle + i * 180)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

part = solid_body
part.name = "pulley_with_keyway"
export_step(part, "output.step")