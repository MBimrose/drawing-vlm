from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
rib_height = 4.0
rib_width = 30.0
rib_thickness = 4.0
hole_diameter = 3.0
hole_edge_margin = 6.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.4
fillet_radius = 0.5

hole_spacing_x = (plate_length - 2 * hole_edge_margin) / (hole_cols - 1)
hole_spacing_y = (plate_width - 2 * hole_edge_margin) / (hole_rows - 1)

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.YZ.offset(-plate_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((-rib_width/2, 0), (rib_width/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=-rib_thickness)
rib = rib_bp.part
rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius)

combined = base + rib

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        combined = combined - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = combined
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")