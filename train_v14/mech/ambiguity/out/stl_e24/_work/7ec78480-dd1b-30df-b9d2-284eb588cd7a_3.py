from build123d import *
import math

inner_radius = 5.0
base_outer_radius = 25.0
convolution_amplitude = 5.0
convolution_height = 8.0
num_convolutions = 6
slot_width = 4.0
slot_depth = 2.0
slot_chamfer = 0.5
total_height = num_convolutions * convolution_height

points = [(inner_radius, 0), (base_outer_radius, 0)]
for i in range(num_convolutions):
    y_mid = (i + 0.5) * convolution_height
    y_next = (i + 1) * convolution_height
    points.append((base_outer_radius + convolution_amplitude, y_mid))
    points.append((base_outer_radius, y_next))
points.append((inner_radius, total_height))

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(*points, close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_radius = base_outer_radius + slot_depth / 2
for i in range(num_convolutions):
    z_pos = (i + 0.5) * convolution_height
    for j in range(6):
        angle_deg = j * 60
        angle_rad = math.radians(angle_deg)
        px = slot_radius * math.cos(angle_rad)
        py = slot_radius * math.sin(angle_rad)
        slot = Pos(px, py, z_pos) * Rot(0, 0, angle_deg) * Box(slot_depth, slot_width, slot_depth)
        slot = chamfer(slot.edges(), slot_chamfer)
        solid_body = solid_body - slot

part = solid_body
part.name = "bellows_with_slots"
export_step(part, "output.step")