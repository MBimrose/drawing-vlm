from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 6.0
rib_width = 5.0
rib_thickness = 4.0
rib_spacing = 12.0
rib_offset_from_end = 8.0
hole_diameter = 5.0
counterbore_diameter = 8.0
counterbore_depth = 2.0
chamfer_distance = 0.5

result = Box(bracket_length, bracket_width, bracket_thickness)

num_ribs = int((bracket_length - 2 * rib_offset_from_end) // rib_spacing) + 1
rib_positions = [(-bracket_length/2 + rib_offset_from_end + i * rib_spacing, 0) for i in range(num_ribs)]

for x, y in rib_positions:
    with BuildPart() as rib_bp:
        with BuildSketch(Plane.XY.offset(bracket_thickness/2)) as sk:
            Rectangle(rib_width, rib_height)
        extrude(amount=rib_height, taper=-10)
    result = result + Pos(x, y, 0) * rib_bp.part

result = result - Cylinder(hole_diameter/2, bracket_thickness + 10)
result = result - Pos(0, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for x, y in [(-bracket_length/2 + rib_offset_from_end, 0), (bracket_length/2 - rib_offset_from_end, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "bracket_with_ribs"
export_step(part, "output.step")