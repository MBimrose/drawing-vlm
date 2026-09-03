from build123d import *

base_length = 80.0
base_width = 40.0
base_thickness = 10.0
rib_height = 8.0
rib_width = 5.0
rib_spacing = 12.0
rib_count = 6
rib_taper = 0.5
hole_diameter = 5.0
hole_offset = 32.0
counterbore_diameter = 8.0
counterbore_depth = 2.0
chamfer_size = 0.5

result = Box(base_length, base_width, base_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    with BuildPart() as rib_bp:
        with BuildSketch(Plane.XY.offset(base_thickness / 2)) as rib_sk:
            Rectangle(rib_width, rib_height)
        extrude(amount=rib_height, taper=rib_taper)
    result = result + rib_bp.part

for x, y in [(-hole_offset, 0), (hole_offset, 0), (0, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, base_thickness + rib_height + 10)

result = result - Pos(0, 0, base_thickness / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

part = result
part.name = "ribbed_plate_with_holes"
export_step(part, "output.step")