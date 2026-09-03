from build123d import *

tri_base = 80.0
tri_height = 60.0
prism_depth = 30.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 24.0
pocket_offset_y = 15.0
hole_diameter = 5.0

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
pocket_box = Box(pocket_width, pocket_depth, pocket_height)
pocket_box = Pos(fc.X + pocket_width/2, fc.Y, fc.Z + pocket_offset_y) * pocket_box
solid_body = solid_body - pocket_box

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
hc = front_face.center()
hole_cyl = Cylinder(hole_diameter/2, prism_depth * 2)
hole_cyl = Pos(hc.X, hc.Y, hc.Z) * hole_cyl
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "triangular_prism_with_pocket_and_hole"
export_step(part, "output.step")