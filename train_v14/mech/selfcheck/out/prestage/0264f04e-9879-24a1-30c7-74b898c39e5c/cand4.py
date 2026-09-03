from build123d import *

outer_radius = 30.0
base_height = 15.0
step_radius = 20.0
step_height = 15.0
inner_radius = 12.0
total_height = 50.0
pocket_width = 10.0
pocket_depth = 8.0
pocket_height = 30.0
pocket_offset_z = 20.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 40.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, base_height))
            l3 = Line(l2@1, (step_radius, base_height))
            l4 = Line(l3@1, (step_radius, base_height + step_height))
            l5 = Line(l4@1, (inner_radius, base_height + step_height))
            l6 = Line(l5@1, (inner_radius, total_height))
            l7 = Line(l6@1, (0, total_height))
            l8 = Line(l7@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(step_radius - pocket_depth/2, 0, pocket_offset_z) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

chamfer_edges = [e for e in solid_body.edges() if abs(e.center().Z - (base_height + step_height)) < 0.5]
solid_body = chamfer(chamfer_edges, chamfer_size)

for y in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)

part = solid_body
part.name = "stepped_spacer"
export_step(part, "output.step")