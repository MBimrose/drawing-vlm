from build123d import *

base_width = 80.0
height = 60.0
length = 30.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 12.0
pocket_offset_x = 10.0
pocket_offset_z = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_width, 0), (base_width / 2, height), close=True)
        make_face()
    extrude(amount=length)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

left_face = solid_body.faces().sort_by(Axis.X)[0]
fc = left_face.center()
pocket_box = Pos(fc.X + pocket_depth/2, fc.Y + pocket_offset_x, fc.Z + pocket_offset_z) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

part = solid_body
part.name = "triangular_prism_with_pocket"
export_step(part, "output.step")