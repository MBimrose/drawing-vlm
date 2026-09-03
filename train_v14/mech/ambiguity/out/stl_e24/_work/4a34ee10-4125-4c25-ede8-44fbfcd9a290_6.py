from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
ring_height = 12.0
fillet_radius = 1.0
pocket_radius = 20.0
pocket_depth = 6.0
slot_width = 4.0
slot_length = 6.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (outer_radius + inner_radius) / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, ring_height))
            l2 = Line(l1 @ 1, (outer_radius, ring_height))
            l3 = Line(l2 @ 1, (outer_radius, 0))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, fillet_radius)
bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = fillet(bottom_edges, fillet_radius)

solid_body = solid_body - Pos(0, 0, ring_height - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, ring_height/2) * Cylinder(mount_hole_diameter/2, ring_height)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = outer_radius * math.cos(angle)
    py = outer_radius * math.sin(angle)
    slot = Pos(px, py, ring_height/4) * Rot(0, 0, math.degrees(angle)) * Box(slot_length, slot_width, ring_height/2)
    solid_body = solid_body - slot

part = solid_body
part.name = "ring_with_pocket_holes_slots"
export_step(part, "output.step")