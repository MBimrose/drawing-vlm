from build123d import *

outer_radius = 30.0
wall_thickness = 8.0
inner_radius = outer_radius - wall_thickness
length = 80.0
slot_width = 6.0
slot_depth = 12.0
slot_length = 20.0
slot_count = 6
slot_angle = 360.0 / slot_count
chamfer_size = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (outer_radius, 0), (outer_radius, length), (inner_radius, length), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(slot_count):
    angle = i * slot_angle
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, length / 2) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    hole = Pos(x, 0, length / 2) * Cylinder(mount_hole_dia / 2, length)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slots"
export_step(part, "output.step")