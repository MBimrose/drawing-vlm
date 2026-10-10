from build123d import *
import math

outer_radius = 45.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 30.0
bevel_height = 5.0
slot_width = 4.0
slot_count = 6
central_hole_diameter = 8.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height - bevel_height))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (outer_radius + wall_thickness, height))
            l4 = Line(l3 @ 1, (outer_radius + wall_thickness, 0))
            l5 = Line(l4 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height * 2)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius + wall_thickness / 2, 0, 0) * Box(wall_thickness * 2, slot_width, height)
    solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "revolved_ring_with_slots"
export_step(part, "output.step")