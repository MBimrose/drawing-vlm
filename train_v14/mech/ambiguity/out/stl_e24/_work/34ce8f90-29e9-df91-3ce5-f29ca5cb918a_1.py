from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_length = 40.0
rib_width = 20.0
rib_height = 4.0
hole_diameter = 4.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
edge_chamfer = 0.8
rib_fillet = 1.2

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s2:
        Rectangle(rib_length, rib_width)
    extrude(amount=rib_height)

solid_body = p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, edge_chamfer)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, rib_fillet)

hole_positions = [
    (-hole_spacing_x, -hole_spacing_y/2),
    (0, -hole_spacing_y/2),
    (hole_spacing_x, -hole_spacing_y/2),
    (-hole_spacing_x, hole_spacing_y/2),
    (0, hole_spacing_y/2),
    (hole_spacing_x, hole_spacing_y/2),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")