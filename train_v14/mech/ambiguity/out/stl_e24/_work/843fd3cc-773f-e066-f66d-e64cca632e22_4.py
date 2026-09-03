from build123d import *
import math

outer_radius = 45.0
inner_radius = 15.0
thickness = 5.0
central_hole_diameter = 9.0
keyway_width = 6.0
keyway_depth = 20.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
mount_hole_count = 3
chamfer_size = 0.6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius)
    extrude(amount=thickness)

solid_body = p.part

# Central through hole
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness * 2)

# Keyway slot
keyway_x = outer_radius - keyway_depth / 2
solid_body = solid_body - Pos(keyway_x, 0, 0) * Box(keyway_width, keyway_depth, thickness * 2)

# Mount holes in polar array
for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, thickness * 2)

# Chamfer all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ring_with_keyway_and_mount_holes"
export_step(part, "output.step")