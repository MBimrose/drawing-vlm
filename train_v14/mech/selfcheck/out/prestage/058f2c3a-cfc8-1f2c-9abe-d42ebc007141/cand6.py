from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 4.0
rib_base_width = 30.0
rib_thickness = 2.0
hole_diameter = 3.0
hole_margin = 6.0
hole_columns = 4
hole_rows = 2
fillet_radius = 0.5

with BuildPart() as p:
    Box(plate_length, plate_width, plate_thickness)
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_base_width/2, 0), (rib_base_width/2, 0), (0, rib_thickness), close=True)
        make_face()
    extrude(amount=-rib_height)

solid_body = p.part

hole_spacing_x = (plate_length - 2*hole_margin) / (hole_columns - 1)
hole_spacing_y = (plate_width - 2*hole_margin) / (hole_rows - 1)

for i in range(hole_columns):
    for j in range(hole_rows):
        x = -plate_length/2 + hole_margin + i*hole_spacing_x
        y = -plate_width/2 + hole_margin + j*hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")