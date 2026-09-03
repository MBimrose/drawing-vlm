from build123d import *

leg_length = 80.0
leg_width = 20.0
thickness = 8.0
flange_width = 28.0
hole_diameter = 6.0
hole_depth = 5.0
hole_offset_x = 30.0
hole_offset_y = 10.0
chamfer_size = 1.0
rib_height = 6.0
rib_width = 5.0
rib_spacing = 15.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_width + flange_width),
                     (0, leg_width + flange_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    x_pos = leg_width + rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_pos, leg_width, thickness - rib_height / 2) * Box(rib_width, thickness, rib_height)
    solid_body = solid_body - rib

hole_x = leg_width + hole_offset_x
hole_y = leg_width + hole_offset_y
cbore = Pos(hole_x, hole_y, thickness - hole_depth / 2) * Cylinder(hole_diameter * 1.5 / 2, hole_depth)
shaft = Pos(hole_x, hole_y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - cbore - shaft

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")