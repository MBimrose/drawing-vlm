from build123d import *
import math

inner_radius = 20.0
wall_thickness = 10.0
outer_radius = inner_radius + wall_thickness
bellows_height = 30.0
num_convolutions = 6
convolution_amplitude = 5.0
central_bore_diameter = 10.0
slot_width = 4.0
slot_depth = wall_thickness * 0.5
slot_count = 6
chamfer_size = 0.5

segment_height = bellows_height / (num_convolutions * 2)
points = [(inner_radius, 0)]
for i in range(1, num_convolutions * 2 + 1):
    y = i * segment_height
    radius = outer_radius if i % 2 == 1 else inner_radius + convolution_amplitude
    points.append((radius, y))
points.append((0, bellows_height))
points.append((0, 0))

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(*points, close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(central_bore_diameter / 2, bellows_height + 2)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_width, slot_depth, bellows_height)
    slot = chamfer(slot.edges(), chamfer_size)
    solid_body = solid_body - slot

part = solid_body
part.name = "bellows"
export_step(part, "output.step")