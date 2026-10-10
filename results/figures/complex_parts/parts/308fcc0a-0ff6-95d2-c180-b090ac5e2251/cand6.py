from build123d import *

outer_radius_bottom = 30.0
outer_radius_top = 35.0
height = 40.0
wall_thickness = 3.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0
flange_height = 5.0
flange_thickness = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius_bottom, 0), (outer_radius_bottom + flange_thickness, 0))
            l2 = Line(l1 @ 1, (outer_radius_bottom + flange_thickness, flange_height))
            l3 = Line(l2 @ 1, (outer_radius_top, height))
            l4 = Line(l3 @ 1, (outer_radius_top - wall_thickness, height))
            l5 = Line(l4 @ 1, (outer_radius_bottom - wall_thickness, flange_height))
            l6 = Line(l5 @ 1, (outer_radius_bottom - wall_thickness, 0))
            l7 = Line(l6 @ 1, (outer_radius_bottom, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = solid_body - Pos(hole_offset, height / 2, height / 2) * Cylinder(hole_diameter / 2, height)

part = solid_body
part.name = "revolved_flange_with_hole"
export_step(part, "output.step")