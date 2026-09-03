from build123d import *
import math

outer_radius = 45.0
inner_radius = 30.0
height = 12.0
split_gap = 2.0
pocket_width = 8.0
pocket_depth = 4.0
pocket_height = 6.0
pocket_count = 4
mount_hole_dia = 4.0
mount_hole_offset = 5.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, height))
            l3 = Line(l2 @ 1, (inner_radius, height))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

split_cut = Pos(0, 0, height / 2) * Box(split_gap, outer_radius * 2, height)
solid_body = solid_body - split_cut

pocket_radius = outer_radius - pocket_depth / 2
for i in range(pocket_count):
    angle = math.radians(i * 360.0 / pocket_count)
    px = pocket_radius * math.cos(angle)
    py = pocket_radius * math.sin(angle)
    pocket = Pos(px, py, pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
    solid_body = solid_body - pocket

hole_radius = (inner_radius + outer_radius) / 2
for i in range(4):
    angle = math.radians(45 + i * 360.0 / 4)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    hole = Pos(px, py, height / 2) * Cylinder(mount_hole_dia / 2, height)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "split_ring_with_pockets"
export_step(part, "output.step")