from build123d import *
import math

outer_radius = 30.0
inner_radius = 8.0
shoulder_radius = 20.0
block_height = 45.0
shoulder_height = 15.0
pocket_width = 12.0
pocket_length = 20.0
pocket_depth = 5.0
hole_diameter = 5.0
hole_depth = 30.0
hole_count = 6
hole_circle_radius = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, block_height - shoulder_height))
            l2 = Line(l1 @ 1, (shoulder_radius, block_height - shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, block_height))
            l4 = Line(l3 @ 1, (inner_radius, block_height))
            l5 = Line(l4 @ 1, (inner_radius, 0))
            l6 = Line(l5 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, block_height - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, block_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_block_with_pocket_and_holes"
export_step(part, "output.step")