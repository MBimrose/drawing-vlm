from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
spline_height = 12.0
spline_points = [
    (plate_length * 0.75, plate_width - spline_height),
    (plate_length * 0.5, plate_width - spline_height * 0.5),
    (plate_length * 0.25, plate_width - spline_height),
    (0, plate_width - spline_height * 0.5)
]
boss_diameter = 30.0
boss_height = 6.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_length, 0))
            l2 = Line(l1 @ 1, (plate_length, plate_width - spline_height))
            s1 = Spline(l2 @ 1, *spline_points)
            l3 = Line(s1 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
tc = top_face.center()
solid_body = solid_body + Pos(tc.X, tc.Y, tc.Z + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = tc.X + (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = tc.Y + (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "spline_plate_with_boss"
export_step(part, "output.step")