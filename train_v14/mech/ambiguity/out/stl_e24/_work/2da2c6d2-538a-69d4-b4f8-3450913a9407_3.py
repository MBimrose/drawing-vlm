from build123d import *

base_diameter = 50.0
top_diameter = 20.0
length = 80.0
central_hole_diameter = 8.0
rib_thickness = 3.0
rib_height = 5.0
rib_position = 30.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(length)) as s2:
        Circle(top_diameter / 2)
    loft()

solid_body = p.part

solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(central_hole_diameter / 2, length)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, length / 2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, length)

rib = Pos(0, 0, rib_position + rib_height / 2) * Cylinder(top_diameter / 2 + rib_thickness, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "lofted_cone_with_rib"
export_step(part, "output.step")