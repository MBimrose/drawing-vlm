from build123d import *
import math

outer_radius = 40.0
wall_thickness = 6.0
inner_radius = outer_radius - wall_thickness
height = 30.0
rib_height = 4.0
rib_width = 6.0
vent_slot_width = 4.0
vent_slot_height = 14.0
vent_slot_count = 6
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, height - rib_height))
            l2 = Line(l1 @ 1, (inner_radius + rib_width, height - rib_height))
            l3 = Line(l2 @ 1, (inner_radius + rib_width, height))
            l4 = Line(l3 @ 1, (outer_radius + rib_width, height))
            l5 = Line(l4 @ 1, (outer_radius + rib_width, 0))
            l6 = Line(l5 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

slot_radius = outer_radius + rib_width / 2
for i in range(vent_slot_count):
    angle = math.radians(i * 360.0 / vent_slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, height / 2 - vent_slot_height / 2) * Box(wall_thickness + 0.01, vent_slot_width, vent_slot_height)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")