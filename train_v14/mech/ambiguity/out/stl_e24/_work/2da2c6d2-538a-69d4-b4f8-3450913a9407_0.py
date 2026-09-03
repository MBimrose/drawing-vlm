from build123d import *

total_length = 80.0
base_diameter = 50.0
top_diameter = 25.0
base_radius = base_diameter / 2.0
top_radius = top_diameter / 2.0
section_count = 8
section_height = total_length / section_count
radius_step = (base_radius - top_radius) / section_count
central_hole_diameter = 8.0
side_hole_diameter = 4.0
side_hole_spacing = 30.0
chamfer_size = 0.5
rib_width = 6.0
rib_height = 12.0
rib_thickness = 4.0

with BuildPart() as p:
    for i in range(section_count + 1):
        z = i * section_height
        r = base_radius - i * radius_step
        with BuildSketch(Plane.XY.offset(z)) as s:
            Circle(r)
    loft()

solid_body = p.part
solid_body = solid_body - Pos(0, 0, total_length / 2) * Cylinder(central_hole_diameter / 2, total_length)

for x in [-side_hole_spacing / 2, side_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, total_length / 2) * Rot(90, 0, 0) * Cylinder(side_hole_diameter / 2, total_length)

rib = Pos(base_radius - rib_thickness / 2, 0, total_length / 2) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "tapered_loft_with_holes_and_rib"
export_step(part, "output.step")