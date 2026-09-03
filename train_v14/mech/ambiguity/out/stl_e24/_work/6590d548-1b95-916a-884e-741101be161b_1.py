from build123d import *

base_radius = 30.0
top_width = 40.0
top_height = 20.0
total_height = 60.0
pocket_width = 20.0
pocket_height = 8.0
pocket_depth = 10.0
hole_diameter = 4.0
hole_spacing = 25.0
hole_offset_y = 15.0
chamfer_size = 2.0
rib_thickness = 5.0
rib_height = 10.0
rib_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(total_height)) as s2:
        Rectangle(top_width, top_height)
    loft()

solid_body = p.part

pocket = Pos(0, 0, total_height - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    hole = Pos(x, y, total_height/2) * Cylinder(hole_diameter/2, total_height + 10)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib = Pos(0, top_height/2 - rib_offset, total_height - rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "lofted_body_with_pocket_holes_rib"
export_step(part, "output.step")