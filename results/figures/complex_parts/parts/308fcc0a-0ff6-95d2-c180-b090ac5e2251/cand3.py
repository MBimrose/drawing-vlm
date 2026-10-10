from build123d import *

outer_radius = 30.0
inner_radius = 25.0
base_height = 10.0
taper_height = 30.0
total_height = base_height + taper_height
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, base_height))
            l3 = Line(l2 @ 1, (outer_radius + 5, total_height))
            l4 = Line(l3 @ 1, (0, total_height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

inner_cavity = Pos(0, 0, total_height / 2) * Cylinder(inner_radius, total_height)
solid_body = solid_body - inner_cavity

hole = Pos(hole_offset, total_height / 2, total_height / 2) * Cylinder(hole_diameter / 2, total_height)
solid_body = solid_body - hole

part = solid_body
part.name = "revolved_cup_with_hole"
export_step(part, "output.step")