from build123d import *

base_length = 80.0
tri_height = 60.0
prism_thickness = 30.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_height = 24.0
pocket_depth = 12.0
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_y = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_length, 0))
            l2 = Line(l1 @ 1, (base_length / 2, tri_height))
            l3 = Line(l2 @ 1, (0, 0))
        make_face()
    extrude(amount=prism_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket_box = Pos(pocket_depth / 2, 0, prism_thickness / 2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

hole_cyl = Pos(hole_offset_x, hole_offset_y, prism_thickness / 2) * Cylinder(hole_diameter / 2, prism_thickness + 10)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "triangular_prism_with_pocket_and_hole"
export_step(part, "output.step")