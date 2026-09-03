from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 80.0
groove_width = 6.0
groove_depth = 2.0
groove_position = 40.0
set_screw_diameter = 5.0
set_screw_depth = 8.0
set_screw_position = 60.0
chamfer_size = 1.0
relief_width = 4.0
relief_depth = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (inner_radius, groove_position),
                     (inner_radius + groove_depth, groove_position),
                     (inner_radius + groove_depth, groove_position + groove_width),
                     (inner_radius, groove_position + groove_width),
                     (inner_radius, length),
                     (outer_radius, length),
                     (outer_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

set_screw_cyl = Pos(outer_radius - set_screw_depth / 2, set_screw_depth / 2, set_screw_position) * Rot(90, 0, 0) * Cylinder(set_screw_diameter / 2, set_screw_depth)
solid_body = solid_body - set_screw_cyl

relief_box = Pos(inner_radius + groove_depth / 2, groove_position + groove_width / 2, length / 2) * Box(relief_width, groove_width, relief_depth)
solid_body = solid_body - relief_box

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "grooved_cylinder_with_set_screw"
export_step(part, "output.step")