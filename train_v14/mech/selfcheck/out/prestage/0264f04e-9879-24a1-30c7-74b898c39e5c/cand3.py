from build123d import *

base_radius = 30.0
base_height = 15.0
middle_radius = 20.0
middle_height = 15.0
top_radius = 12.0
top_height = 20.0
boss_radius = 6.0
boss_height = 5.0
groove_width = 2.0
groove_depth = 1.5
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 0.8

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (middle_radius, base_height))
            l4 = Line(l3@1, (middle_radius, base_height + middle_height))
            l5 = Line(l4@1, (top_radius, base_height + middle_height))
            l6 = Line(l5@1, (top_radius, base_height + middle_height + top_height))
            l7 = Line(l6@1, (0, base_height + middle_height + top_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, base_height + middle_height + top_height + boss_height/2) * Cylinder(boss_radius, boss_height)

groove_z = base_height + middle_height / 2 - groove_depth / 2
solid_body = solid_body - Pos(0, 0, groove_z) * Cylinder(middle_radius - groove_width, groove_depth)

for x, y in [(0, -hole_spacing/2), (0, hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "stepped_cylinder_with_boss"
export_step(part, "output.step")