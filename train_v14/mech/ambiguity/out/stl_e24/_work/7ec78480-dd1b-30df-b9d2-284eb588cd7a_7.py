from build123d import *
import math

inner_radius = 5.0
outer_radius = 20.0
corrugation_amplitude = 10.0
bellows_length = 40.0
num_corrugations = 4
spline_tooth_depth = 2.0
spline_tooth_width = 4.0
spline_tooth_count = 6
vent_slot_width = 5.0
vent_slot_height = 8.0
vent_slot_count = 6
chamfer_size = 0.5

segment_length = bellows_length / (num_corrugations * 2)
points = [(inner_radius, 0.0)]
for i in range(1, num_corrugations * 2 + 1):
    z = i * segment_length
    radius = outer_radius + corrugation_amplitude if i % 2 == 1 else outer_radius
    points.append((radius, z))
points.append((inner_radius, bellows_length))

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(*points, close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_radius, bellows_length + 2)

tooth_radius = inner_radius - spline_tooth_depth
for i in range(spline_tooth_count):
    angle = i * 360.0 / spline_tooth_count
    tooth = Rot(0, 0, angle) * Pos(tooth_radius, 0, 0) * Box(spline_tooth_depth * 2, spline_tooth_width, bellows_length)
    solid_body = solid_body - tooth

slot_radius = outer_radius + corrugation_amplitude / 2
for i in range(vent_slot_count):
    angle = i * 360.0 / vent_slot_count
    slot = Rot(0, 0, angle) * Pos(slot_radius, 0, 0) * Box(vent_slot_width, vent_slot_height, corrugation_amplitude)
    slot = chamfer(slot.edges(), chamfer_size)
    solid_body = solid_body - slot

part = solid_body
part.name = "bellows"
export_step(part, "output.step")