from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 30.0
rib_thickness = 4.0
rib_offset = 5.0
hole_diameter = 3.0
hole_margin = 6.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.4
boss_diameter = 12.0
boss_height = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as rib_sk:
        with BuildLine() as rib_line:
            l1 = Line((-rib_height/2, 0), (rib_height/2, 0))
            l2 = Line(l1@1, (0, rib_thickness))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-rib_thickness)
solid_body = solid_body + rib_bp.part

solid_body = solid_body + Pos(0, 0, plate_thickness/2) * Cylinder(boss_diameter/2, boss_height)

x_start = -plate_length/2 + hole_margin
x_end = plate_length/2 - hole_margin
y_start = -plate_width/2 + hole_margin
y_end = plate_width/2 - hole_margin
x_spacing = (x_end - x_start) / (hole_cols - 1) if hole_cols > 1 else 0
y_spacing = (y_end - y_start) / (hole_rows - 1) if hole_rows > 1 else 0

for i in range(hole_cols):
    for j in range(hole_rows):
        x = x_start + i * x_spacing
        y = y_start + j * y_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

part = solid_body
part.name = "plate_with_rib_boss_and_holes"
export_step(part, "output.step")