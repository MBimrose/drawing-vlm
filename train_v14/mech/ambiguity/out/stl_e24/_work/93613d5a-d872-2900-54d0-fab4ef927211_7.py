from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_distance = 1.0
spline_points = [
    (plate_length * 0.75, plate_width * 1.1),
    (plate_length * 0.5, plate_width * 0.9),
    (plate_length * 0.25, plate_width * 1.1),
    (0, plate_width)
]

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (plate_length, 0))
            l2 = Line(l1 @ 1, (plate_length, plate_width))
            s1 = Spline(l2 @ 1, *spline_points)
            l3 = Line(s1 @ 1, (0, 0))
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body + Pos(plate_length/2, plate_width/2, plate_thickness) * Cylinder(boss_diameter/2, boss_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = plate_length/2 + (i - (hole_cols-1)/2) * hole_spacing_x
        y = plate_width/2 + (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")