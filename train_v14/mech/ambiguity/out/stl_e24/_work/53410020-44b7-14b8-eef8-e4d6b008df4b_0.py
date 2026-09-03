from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 40.0
thickness = 12.0
keyway_width = 6.0
keyway_length = 20.0
fillet_radius = 1.5
mount_hole_diameter = 5.0
mount_hole_count = 4
mount_hole_radius = (outer_diameter/2) - 5.0
rib_width = 3.0
rib_height = 6.0
rib_count = 6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
        Circle(inner_diameter/2)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

keyway = Pos(outer_diameter/2 - keyway_length/2, 0, thickness/2) * Box(keyway_length, keyway_width, thickness)
solid_body = solid_body - keyway

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter/2 - rib_width/2, 0, thickness/2) * Box(rib_width, rib_height, thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "ring_with_keyway_and_ribs"
export_step(part, "output.step")