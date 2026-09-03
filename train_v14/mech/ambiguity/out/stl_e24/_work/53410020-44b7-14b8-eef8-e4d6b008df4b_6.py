from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
thickness = 12.0
keyway_width = 6.0
keyway_length = 20.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_count = 4
mount_hole_radius = 25.0
rib_thickness = 3.0
rib_height = 6.0
rib_count = 6
relief_width = 10.0
relief_length = 15.0
relief_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = solid_body - Pos(outer_diameter/2 - keyway_length/2, 0, thickness/2) * Box(keyway_length, keyway_width, thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Cylinder(mount_hole_dia/2, thickness)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter/2 - rib_thickness/2, 0, thickness/2) * Box(rib_thickness, rib_height, thickness)
    solid_body = solid_body + rib

solid_body = solid_body - Pos(inner_diameter/2 + relief_depth/2, 0, thickness/2) * Box(relief_width, relief_length, thickness)

part = solid_body
part.name = "collar_with_keyway"
export_step(part, "output.step")