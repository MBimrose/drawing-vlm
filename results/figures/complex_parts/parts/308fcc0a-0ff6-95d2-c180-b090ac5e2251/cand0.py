from build123d import *

base_radius = 30.0
top_radius = 35.0
height = 40.0
wall_thickness = 3.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((base_radius, 0), (base_radius, height * 0.2))
            l2 = Line(l1 @ 1, (top_radius, height))
            l3 = Line(l2 @ 1, (top_radius - wall_thickness, height))
            l4 = Line(l3 @ 1, (base_radius - wall_thickness, height * 0.2))
            l5 = Line(l4 @ 1, (base_radius - wall_thickness, 0))
            l6 = Line(l5 @ 1, (base_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = solid_body - Pos(hole_offset, height * 0.6, 0) * Cylinder(hole_diameter / 2, height * 2)

part = solid_body
part.name = "revolved_cup_with_hole"
export_step(part, "output.step")