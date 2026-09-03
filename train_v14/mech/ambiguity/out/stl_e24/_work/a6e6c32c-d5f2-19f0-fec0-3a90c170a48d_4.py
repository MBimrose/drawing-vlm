from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 5.0
corner_radius = 6.0
edge_chamfer = 0.7
rib_height = 2.0
rib_width = 4.0
rib_spacing = 12.0
rib_count = 4
hole_diameter = 3.0
hole_cbore_diameter = 5.0
hole_cbore_depth = 2.0
hole_offset = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(cover_length, cover_width)
    extrude(amount=cover_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), edge_chamfer)

for i in range(rib_count):
    y_pos = -cover_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(cover_length/2 + rib_height/2, y_pos, cover_thickness/2) * Box(rib_height, rib_width, rib_height)
    solid_body = solid_body + rib

hole_positions = [
    (hole_offset, hole_offset),
    (cover_length - hole_offset, hole_offset),
    (hole_offset, cover_width - hole_offset),
    (cover_length - hole_offset, cover_width - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, cover_thickness - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    solid_body = solid_body - Pos(x, y, cover_thickness/2) * Cylinder(hole_diameter/2, cover_thickness)

part = solid_body
part.name = "cover_plate"
export_step(part, "output.step")