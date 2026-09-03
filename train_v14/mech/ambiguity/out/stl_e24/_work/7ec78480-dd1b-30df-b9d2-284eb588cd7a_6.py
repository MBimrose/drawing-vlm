from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
height = 40.0
corrugation_count = 4
corrugation_amplitude = 2.0
central_hole_diameter = 10.0
slot_width = 4.0
slot_depth = 6.0
slot_count = 6
chamfer_size = 0.5
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 5.0

segment_height = height / (corrugation_count * 2)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l = Line((0, 0), (inner_radius, 0))
            for i in range(corrugation_count):
                l = Line(l @ 1, (outer_radius, (2 * i + 1) * segment_height))
                l = Line(l @ 1, (inner_radius, (2 * i + 2) * segment_height))
            l = Line(l @ 1, (0, height))
            l = Line(l @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height + 2)

slot_radius = (inner_radius + outer_radius) / 2
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, height / 2) * Rot(0, 0, math.degrees(angle)) * Box(slot_depth, slot_width, slot_width)
    solid_body = solid_body - slot

pocket = Pos(0, height / 2, height - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "corrugated_cylinder_with_slots"
export_step(part, "output.step")