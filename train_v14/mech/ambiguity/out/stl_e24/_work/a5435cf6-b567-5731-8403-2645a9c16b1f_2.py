from build123d import *

length = 80.0
outer_width = 40.0
outer_height = 20.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_width = 10.0
rib_height = 30.0
rib_spacing = 12.0
hole_diameter = 5.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(outer_width, outer_height)
    extrude(amount=length)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib_count = int((outer_width - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_offset = -outer_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_offset, 0, rib_height/2) * Box(rib_thickness, rib_width, rib_height)
    solid_body = solid_body + rib

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    hole = Pos(x, y, length/2) * Cylinder(hole_diameter/2, length + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_ribs_and_holes"
export_step(part, "output.step")