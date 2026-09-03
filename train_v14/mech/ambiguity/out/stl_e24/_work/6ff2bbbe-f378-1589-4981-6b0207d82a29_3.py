from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 8.0
rib_width = 6.0
rib_spacing = 12.0
rib_count = int((bracket_length - 2 * rib_spacing) / rib_spacing)
rib_draft_angle = 5.0
hole_diameter = 5.0
hole_offset = 8.0
counterbore_diameter = 10.0
counterbore_depth = 2.0
chamfer_size = 0.5

result = Box(bracket_length, bracket_width, bracket_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    x_pos = -bracket_length / 2 + rib_spacing + i * rib_spacing
    with BuildPart() as rib_bp:
        with BuildSketch() as rib_sk:
            Rectangle(rib_width, rib_height)
        extrude(amount=rib_height, taper=rib_draft_angle)
    result = result + Pos(x_pos, 0, bracket_thickness / 2) * rib_bp.part

hole_positions = [(-bracket_length / 2 + hole_offset, 0), (0, 0), (bracket_length / 2 - hole_offset, 0)]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness + 1)

result = result - Pos(0, 0, bracket_thickness / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

part = result
part.name = "bracket_with_ribs"
export_step(part, "output.step")