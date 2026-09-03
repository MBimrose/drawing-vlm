from build123d import *
import math

outer_radius = 30.0
inner_radius = 8.0
length = 80.0
slot_width = 6.0
slot_depth = 12.0
slot_length = 20.0
num_slots = 6
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, -length/2), (outer_radius, length/2), (inner_radius, length/2), (inner_radius, -length/2), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(num_slots):
    angle_deg = i * 360.0 / num_slots
    angle_rad = math.radians(angle_deg)
    px = (outer_radius - slot_depth/2) * math.cos(angle_rad)
    py = (outer_radius - slot_depth/2) * math.sin(angle_rad)
    slot = Pos(px, py, 0) * Rot(0, 0, angle_deg) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_cylinder_with_slots"
export_step(part, "output.step")