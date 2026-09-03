from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 8.0
rib_height = 4.0
rib_width = 6.0
hex_flat_distance = 10.0
hex_depth = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 0.5

base = Box(arm_length, arm_width, arm_thickness)
rib = Box(arm_length, rib_width, rib_height)
solid_body = base + rib

with BuildPart() as hex_bp:
    with BuildSketch() as hex_sk:
        RegularPolygon(hex_flat_distance/2, 6)
    extrude(amount=hex_depth)
hex_prism = Pos(0, 0, arm_thickness/2 - hex_depth/2) * hex_bp.part
solid_body = solid_body - hex_prism

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, arm_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "arm_with_rib_and_hex_cut"
export_step(part, "output.step")