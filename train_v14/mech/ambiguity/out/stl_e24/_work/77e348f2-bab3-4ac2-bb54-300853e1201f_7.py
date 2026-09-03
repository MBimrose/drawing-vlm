from build123d import *

base_width = 80.0
height = 60.0
length = 30.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 24.0
pocket_offset = 5.0
hole_diameter = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-base_width/2, 0), (base_width/2, 0))
            l2 = Line(l1@1, (0, height))
            l3 = Line(l2@1, (-base_width/2, 0))
        make_face()
    extrude(amount=length)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

left_face = solid_body.faces().sort_by(Axis.X)[0]
fc = left_face.center()
pocket_box = Box(pocket_width, pocket_depth, pocket_height)
pocket_box = Pos(fc.X + pocket_width/2, fc.Y + pocket_depth/2, fc.Z + pocket_offset) * pocket_box
solid_body = solid_body - pocket_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
tc = top_face.center()
hole_cyl = Cylinder(hole_diameter/2, length * 2)
hole_cyl = Pos(tc.X, tc.Y, tc.Z) * hole_cyl
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "triangular_prism_with_pocket_and_hole"
export_step(part, "output.step")