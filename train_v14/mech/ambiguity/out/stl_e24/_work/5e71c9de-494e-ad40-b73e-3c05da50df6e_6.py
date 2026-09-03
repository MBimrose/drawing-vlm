from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
edge_fillet_radius = 3.0
central_pocket_diameter = 30.0
central_pocket_depth = 2.0
hole_diameter = 8.0
hole_offset = 15.0
rib_width = 10.0
rib_height = 6.0
rib_thickness = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness - central_pocket_depth / 2) * Cylinder(central_pocket_diameter / 2, central_pocket_depth)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness)

rib = Pos(0, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")