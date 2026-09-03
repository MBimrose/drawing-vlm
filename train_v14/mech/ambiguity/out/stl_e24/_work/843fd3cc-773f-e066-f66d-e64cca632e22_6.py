from build123d import *
import math

outer_radius = 45.0
inner_radius = 15.0
thickness = 5.0
slot_width = 6.0
slot_length = 20.0
slot_offset = 30.0
central_hole_diameter = 9.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
chamfer_distance = 0.6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

slot_cut = Pos(slot_offset, 0, thickness/2) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot_cut

central_hole = Pos(0, 0, thickness/2) * Cylinder(central_hole_diameter/2, thickness)
solid_body = solid_body - central_hole

for i in range(3):
    angle = math.radians(i * 120)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    mount_hole = Pos(px, py, thickness/2) * Cylinder(mount_hole_diameter/2, thickness)
    solid_body = solid_body - mount_hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "ring_with_slot_and_holes"
export_step(part, "output.step")