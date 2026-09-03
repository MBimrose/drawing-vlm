from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 80.0
groove_depth = 2.0
groove_width = 5.0
groove_position = 50.0
radial_hole_diameter = 5.0
radial_hole_offset = 22.0
radial_hole_position = 65.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, groove_position))
            l2 = Line(l1@1, (inner_radius + groove_depth, groove_position))
            l3 = Line(l2@1, (inner_radius + groove_depth, groove_position + groove_width))
            l4 = Line(l3@1, (inner_radius, groove_position + groove_width))
            l5 = Line(l4@1, (inner_radius, length))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (outer_radius, 0))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
hole_cyl = Pos(radial_hole_offset, 0, radial_hole_position) * Rot(90, 0, 0) * Cylinder(radial_hole_diameter / 2, outer_radius * 2)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "revolved_grooved_cylinder_with_radial_hole"
export_step(part, "output.step")