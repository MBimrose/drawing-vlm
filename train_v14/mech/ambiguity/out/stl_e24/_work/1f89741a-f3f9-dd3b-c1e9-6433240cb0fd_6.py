from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 8.0
rib_width = 20.0
rib_height = 4.0
rib_thickness = 2.0
hole_diameter = 6.0
countersink_diameter = 12.0
countersink_angle = 82.0
hole_spacing = 30.0
fillet_radius = 1.0
pocket_margin = 5.0
pocket_depth = 4.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
rib = Pos(0, 0, base_thickness + rib_height/2) * Box(rib_width, base_width, rib_height)
solid_body = base + rib

pocket_w = base_length - 2 * pocket_margin
pocket_h = base_width - 2 * pocket_margin
pocket = Pos(0, 0, base_thickness + rib_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

total_h = base_thickness + rib_height
for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    csk = Pos(x, y, total_h) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, total_h, countersink_angle)
    solid_body = solid_body - csk

part = solid_body
part.name = "base_plate_with_rib"
export_step(part, "output.step")