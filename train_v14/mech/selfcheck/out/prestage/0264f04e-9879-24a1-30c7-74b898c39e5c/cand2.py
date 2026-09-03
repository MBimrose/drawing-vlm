from build123d import *

base_radius = 30.0
step1_radius = 20.0
step2_radius = 12.0
base_height = 15.0
step1_height = 15.0
step2_height = 20.0
total_height = base_height + step1_height + step2_height
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1@1, (base_radius, base_height))
            l3 = Line(l2@1, (step1_radius, base_height))
            l4 = Line(l3@1, (step1_radius, base_height + step1_height))
            l5 = Line(l4@1, (step2_radius, base_height + step1_height))
            l6 = Line(l5@1, (step2_radius, total_height))
            l7 = Line(l6@1, (0, total_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

# Chamfer edges at step transitions (exclude top and bottom faces)
all_edges = solid_body.edges()
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
top_edges = top_face.edges()
bottom_edges = bottom_face.edges()
step_edges = [e for e in all_edges if e not in top_edges and e not in bottom_edges]
solid_body = chamfer(step_edges, chamfer_size)

# Mounting holes on base
for x, y in [(0, mount_hole_offset), (0, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, total_height + 10)

part = solid_body
part.name = "stepped_cylinder_with_mounting_holes"
export_step(part, "output.step")