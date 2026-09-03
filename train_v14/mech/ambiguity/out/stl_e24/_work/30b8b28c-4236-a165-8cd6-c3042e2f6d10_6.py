from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
pocket_diameter = 20.0
pocket_depth = 0.3
slot_width = 1.5
slot_length = 5.0
slot_count = 8
chamfer_size = 0.2

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
pocket_radius = pocket_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, thickness))
            l3 = Line(l2@1, (inner_radius, thickness))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

pocket = Pos(0, 0, thickness - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

slot_radius = outer_radius - slot_length/2.0
for i in range(slot_count):
    angle_deg = i * 360.0 / slot_count
    angle_rad = math.radians(angle_deg)
    px = slot_radius * math.cos(angle_rad)
    py = slot_radius * math.sin(angle_rad)
    slot = Pos(px, py, thickness/2) * Rot(0, 0, angle_deg) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

part = solid_body
part.name = "ring_with_pocket_and_slots"
export_step(part, "output.step")