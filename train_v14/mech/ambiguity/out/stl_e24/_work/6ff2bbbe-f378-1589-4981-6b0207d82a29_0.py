from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 12.0
rib_taper = 0.5
counterbore_diameter = 8.0
counterbore_depth = 2.0
through_hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
chamfer_size = 0.5

result = Box(bracket_length, bracket_width, bracket_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((bracket_length - 2 * mount_hole_offset) // rib_spacing) + 1
rib_positions = [(-bracket_length/2 + mount_hole_offset + i * rib_spacing, 0) for i in range(rib_count)]

for x, y in rib_positions:
    with BuildPart() as rib_bp:
        with BuildSketch(Plane.XY.offset(bracket_thickness/2)) as sk:
            Rectangle(rib_width, rib_height)
        extrude(amount=rib_height, taper=rib_taper)
    result = result + rib_bp.part

result = result - Pos(0, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - Cylinder(through_hole_diameter/2, bracket_thickness + 10)

mount_points = [(-bracket_length/2 + mount_hole_offset, 0), (bracket_length/2 - mount_hole_offset, 0)]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 10)

part = result
part.name = "bracket_with_ribs"
export_step(part, "output.step")