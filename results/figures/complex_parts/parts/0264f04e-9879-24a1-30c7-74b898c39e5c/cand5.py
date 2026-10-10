from build123d import *

base_radius = 30.0
step1_radius = 20.0
step2_radius = 12.0
base_height = 15.0
step1_height = 15.0
step2_height = 20.0
total_height = base_height + step1_height + step2_height
chamfer_size = 1.0
hole_diameter = 5.0
hole_offset = 20.0
pocket_width = 8.0
pocket_depth = 4.0
pocket_height = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_height))
            l3 = Line(l2 @ 1, (step1_radius, base_height))
            l4 = Line(l3 @ 1, (step1_radius, base_height + step1_height))
            l5 = Line(l4 @ 1, (step2_radius, base_height + step1_height))
            l6 = Line(l5 @ 1, (step2_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

for x, y in [(0, hole_offset), (0, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 10)

pocket = Pos(step2_radius - pocket_depth / 2, 0, total_height - pocket_height / 2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "stepped_shaft_with_holes_and_pocket"
export_step(part, "output.step")