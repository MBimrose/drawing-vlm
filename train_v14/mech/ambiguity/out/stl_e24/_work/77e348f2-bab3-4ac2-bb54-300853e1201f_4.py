from build123d import *

base_width = 80.0
tri_height = 60.0
prism_length = 30.0
fillet_radius = 2.0
pocket_width = 20.0
pocket_height = 24.0
pocket_depth = 12.0
pocket_offset_y = 12.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_y = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_width, 0), (base_width / 2, tri_height), close=True)
        make_face()
    extrude(amount=prism_length)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

x_face = solid_body.faces().sort_by(Axis.X)[0]
fc = x_face.center()
pocket_box = Pos(fc.X + pocket_depth / 2, fc.Y + pocket_offset_y, fc.Z) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

for i in range(2):
    hx = fc.X + (i - 0.5) * hole_spacing
    hy = fc.Y + hole_offset_y
    hz = fc.Z
    hole = Pos(hx, hy, hz) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, prism_length * 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "triangular_prism_with_pocket_and_holes"
export_step(part, "output.step")