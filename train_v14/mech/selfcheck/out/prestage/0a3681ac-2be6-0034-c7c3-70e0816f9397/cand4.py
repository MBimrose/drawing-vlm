from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
rib_height = 6.0
rib_width = 10.0
hole_diameter = 8.0
hole_offset_x = 15.0
hole_offset_y = 0.0
fillet_radius = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0
pocket_offset_x = 30.0
pocket_offset_y = 0.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

pocket_x = pocket_offset_x - bracket_length / 2
pocket_y = pocket_offset_y
pocket_z = bracket_thickness - pocket_depth / 2
solid_body = solid_body - Pos(pocket_x, pocket_y, pocket_z) * Box(pocket_length, pocket_width, pocket_depth)

hole_x = hole_offset_x
hole_y = hole_offset_y
solid_body = solid_body - Pos(hole_x, hole_y, bracket_thickness / 2) * Cylinder(hole_diameter / 2, bracket_thickness)

with BuildPart() as rib_p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-rib_width / 2, 0), (rib_width / 2, 0))
            l2 = Line(l1 @ 1, (0, rib_height))
            l3 = Line(l2 @ 1, (-rib_width / 2, 0))
        make_face()
    extrude(amount=bracket_thickness)

rib = rib_p.part
rib = Pos(0, bracket_width / 2, 0) * rib
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "bracket_with_rib"
export_step(part, "output.step")