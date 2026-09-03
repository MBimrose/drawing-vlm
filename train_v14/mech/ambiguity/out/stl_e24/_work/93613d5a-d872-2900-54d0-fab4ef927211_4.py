from build123d import *

base_width = 80.0
base_depth = 60.0
base_thickness = 8.0
spline_height = 12.0
boss_diameter = 30.0
boss_height = 6.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_size = 1.0

spline_pts = [
    (base_width, base_depth),
    (base_width * 0.75, base_depth + spline_height * 0.6),
    (base_width * 0.5, base_depth + spline_height * 0.3),
    (base_width * 0.25, base_depth + spline_height * 0.8),
    (0, base_depth)
]

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_width, 0))
            l2 = Line(l1 @ 1, (base_width, base_depth))
            s1 = Spline(*spline_pts)
            l3 = Line(s1 @ 1, (0, 0))
        make_face()
    extrude(amount=base_thickness)

solid_body = p.part

for i in range(hole_cols):
    for j in range(hole_rows):
        x = base_width / 2 + (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = base_depth / 2 + (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, base_thickness / 2) * Cylinder(hole_diameter / 2, base_thickness + 1)

solid_body = solid_body + Pos(base_width / 2, base_depth / 2, base_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_spline"
export_step(part, "output.step")