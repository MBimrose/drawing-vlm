from build123d import *

tube_length = 100.0
outer_radius = 20.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
groove_width = 5.0
groove_depth = 1.5
groove_spacing = 12.0
num_grooves = 3
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, tube_length))
            l2 = Line(l1@1, (inner_radius, tube_length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

for i in range(num_grooves):
    z_pos = tube_length / 2 + i * groove_spacing
    groove = Pos(outer_radius - groove_depth / 2, 0, z_pos) * Box(groove_width, groove_depth, tube_length / 3)
    solid_body = solid_body - groove

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "tube_with_grooves"
export_step(part, "output.step")