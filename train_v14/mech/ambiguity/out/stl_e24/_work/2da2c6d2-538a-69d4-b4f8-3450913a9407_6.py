from build123d import *

base_radius = 25.0
top_radius = 12.5
length = 80.0
bore_radius = 4.0
chamfer_size = 0.5
mount_hole_radius = 2.0
mount_hole_spacing = 30.0
tab_width = 15.0
tab_height = 10.0
tab_thickness = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(length)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length/2) * Cylinder(bore_radius, length)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, length/2) * Rot(90, 0, 0) * Cylinder(mount_hole_radius, length)

tab = Pos(base_radius/2, 0, tab_thickness/2) * Box(tab_width, tab_height, tab_thickness)
solid_body = solid_body + tab

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "tapered_body_with_bore_and_tabs"
export_step(part, "output.step")