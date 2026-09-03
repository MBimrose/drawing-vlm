from build123d import *

base_radius = 25.0
top_radius = 12.0
height = 80.0
central_hole_diameter = 8.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(height)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part

solid_body = solid_body - Pos(0, 0, height/2) * Cylinder(central_hole_diameter/2, height)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "lofted_cone_with_holes"
export_step(part, "output.step")