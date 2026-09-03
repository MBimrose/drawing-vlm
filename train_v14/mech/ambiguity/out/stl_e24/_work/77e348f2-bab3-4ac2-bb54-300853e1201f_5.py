from build123d import *

base_width = 80.0
height = 60.0
length = 30.0
fillet_radius = 2.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 24.0
pocket_offset_from_base = 15.0

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

pocket_center_x = -base_width/2 + pocket_offset_from_base
pocket_center_y = 0
pocket_center_z = length/2

pocket_box = Box(pocket_width, pocket_depth, pocket_height)
pocket_box = Pos(pocket_center_x, pocket_center_y + pocket_depth/2, pocket_center_z) * pocket_box

solid_body = solid_body - pocket_box

part = solid_body
part.name = "triangular_prism_with_pocket"
export_step(part, "output.step")