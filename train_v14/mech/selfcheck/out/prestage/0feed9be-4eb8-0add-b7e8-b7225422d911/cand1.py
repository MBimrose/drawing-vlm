from build123d import *

outer_radius = 30
inner_radius = 20
body_height = 70
wall_thickness = outer_radius - inner_radius
counterbore_diameter = 12
counterbore_depth = 10
fillet_radius = 2
groove_depth = 2
groove_width = 2
groove_position = 20
mount_hole_diameter = 5
mount_hole_offset = 5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, body_height))
            l2 = Line(l1@1, (inner_radius, body_height))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

solid_body = solid_body - Pos(0, 0, body_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

groove_r = inner_radius - groove_depth
solid_body = solid_body - Pos(0, 0, groove_position + groove_width/2) * Cylinder(groove_r, groove_width)

hole_r = mount_hole_diameter / 2
hole_h = body_height + 2
for x in [outer_radius - mount_hole_offset, -(outer_radius - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, 0, body_height/2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "hollow_cylinder_with_features"
export_step(part, "output.step")