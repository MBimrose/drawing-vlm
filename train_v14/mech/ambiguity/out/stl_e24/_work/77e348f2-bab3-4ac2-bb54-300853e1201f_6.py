from build123d import *

tri_base = 80.0
tri_height = 60.0
prism_depth = 30.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 24.0
pocket_offset_x = 5.0
pocket_offset_y = 5.0
hole_diameter = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (tri_base, 0), (tri_base/2, tri_height), close=True)
        make_face()
    extrude(amount=prism_depth)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

left_face = solid_body.faces().sort_by(Axis.X)[0]
fc = left_face.center()
pocket_box = Pos(fc.X + pocket_depth/2, fc.Y + pocket_offset_x, fc.Z + pocket_offset_y) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
tc = top_face.center()
hole_cyl = Pos(tc.X, tc.Y, tc.Z) * Cylinder(hole_diameter/2, prism_depth * 2)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "triangular_prism_with_pocket_and_hole"
export_step(part, "output.step")