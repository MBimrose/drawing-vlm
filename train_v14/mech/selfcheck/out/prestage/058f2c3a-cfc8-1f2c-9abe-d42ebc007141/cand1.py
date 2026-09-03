from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 30.0
rib_thickness = 4.0
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_margin = 6.0
chamfer_size = 0.4

with BuildPart() as p:
    Box(plate_length, plate_width, plate_thickness)
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-rib_height/2, 0), (rib_height/2, 0))
            l2 = Line(l1@1, (0, rib_thickness))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-rib_thickness)

solid = p.part
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

x_spacing = (plate_length - 2*hole_margin) / (hole_cols - 1)
y_spacing = (plate_width - 2*hole_margin) / (hole_rows - 1)
for i in range(hole_cols):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_margin + i * x_spacing
        y = -plate_width/2 + hole_margin + j * y_spacing
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")