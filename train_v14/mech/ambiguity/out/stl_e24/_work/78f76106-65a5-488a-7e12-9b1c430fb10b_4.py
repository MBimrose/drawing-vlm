from build123d import *

shaft_length = 80.0
base_radius = 15.0
tip_radius = 10.0
base_fillet_radius = 5.0
tip_chamfer = 2.0
hole_diameter = 12.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 6.0
flange_thickness = 10.0
flange_radius = base_radius

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, base_radius))
            l2 = Line(l1 @ 1, (shaft_length, tip_radius))
            l3 = Line(l2 @ 1, (shaft_length, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.X)

solid_body = p.part

base_edges = solid_body.edges().sort_by(Axis.X)[:1]
solid_body = fillet(base_edges, base_fillet_radius)

tip_edges = solid_body.edges().sort_by(Axis.X)[-1:]
solid_body = chamfer(tip_edges, tip_chamfer)

solid_body = solid_body - Cylinder(hole_diameter / 2, shaft_length + 2 * base_radius)

pocket = Pos(shaft_length / 4, 0, pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

flange = Pos(shaft_length + flange_thickness / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(flange_radius, flange_thickness)
solid_body = solid_body + flange

part = solid_body
part.name = "tapered_shaft_with_flange"
export_step(part, "output.step")