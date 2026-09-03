from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 40.0
counterbore_diameter = 40.0
counterbore_depth = 10.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_radius = 35.0
rib_width = 6.0
rib_height = 3.0
slot_width = 12.0
slot_length = 20.0
slot_depth = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_diameter/2, 0), (outer_diameter/2, height))
            l2 = Line(l1@1, (inner_diameter/2, height))
            l3 = Line(l2@1, (inner_diameter/2, counterbore_depth))
            l4 = Line(l3@1, (counterbore_diameter/2, counterbore_depth))
            l5 = Line(l4@1, (counterbore_diameter/2, 0))
            l6 = Line(l5@1, (outer_diameter/2, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_distance)

for i in range(3):
    a = math.radians(i * 120.0)
    px = mount_hole_radius * math.cos(a)
    py = mount_hole_radius * math.sin(a)
    solid_body = solid_body - Pos(px, py, height/2) * Cylinder(mount_hole_diameter/2, height)

rib = Pos(outer_diameter/2 - rib_width/2, 0, height/2) * Box(rib_width, rib_height, height)
for i in range(3):
    solid_body = solid_body + Rot(0, 0, i * 120) * rib

slot = Pos(0, 0, height - slot_depth/2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "spacer_with_ribs"
export_step(part, "output.step")