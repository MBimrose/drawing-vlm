from build123d import *

base_length = 100.0
base_width = 60.0
base_thickness = 8.0
rib_height = 30.0
rib_width = 20.0
rib_length = 80.0
rib_taper_angle = 5.0
pocket_length = 60.0
pocket_width = 12.0
pocket_depth = 4.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XY.offset(base_thickness)) as sk:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height, taper=rib_taper_angle)

result = base + rib_bp.part

pocket = Pos(0, 0, base_thickness + rib_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_positions = [
    (-base_length / 2 + mount_hole_offset, -base_width / 2 + mount_hole_offset),
    (base_length / 2 - mount_hole_offset, -base_width / 2 + mount_hole_offset),
    (-base_length / 2 + mount_hole_offset, base_width / 2 - mount_hole_offset),
    (base_length / 2 - mount_hole_offset, base_width / 2 - mount_hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness / 2) * Cylinder(mount_hole_diameter / 2, base_thickness + 1)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "base_plate_with_rib"
export_step(part, "output.step")