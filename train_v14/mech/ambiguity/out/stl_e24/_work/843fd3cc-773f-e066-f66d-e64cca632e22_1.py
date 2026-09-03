from build123d import *
import math

outer_radius = 45.0
inner_radius = 15.0
thickness = 5.0
central_hole_dia = 9.0
mount_hole_dia = 5.0
mount_hole_radius = 30.0
keyway_width = 6.0
keyway_length = 20.0
chamfer_size = 0.6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

# Central through hole
solid_body = solid_body - Cylinder(central_hole_dia/2, thickness * 2)

# Mount holes at 3 points on circle
for i in range(3):
    angle = math.radians(i * 120)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_dia/2, thickness * 2)

# Keyway slot
keyway_x = outer_radius - keyway_length/2 - 5
solid_body = solid_body - Pos(keyway_x, 0, 0) * Box(keyway_width, keyway_length, thickness * 2)

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ring_with_holes_and_keyway"
export_step(part, "output.step")