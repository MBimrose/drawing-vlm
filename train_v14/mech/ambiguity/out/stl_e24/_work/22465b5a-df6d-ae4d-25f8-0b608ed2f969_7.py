from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
length = 80.0
inlet_radius = 10.0
inlet_length = 15.0
inlet_offset = 5.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
mount_hole_count = 3

inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

inlet = Pos(outer_radius + inlet_length/2, 0, inlet_offset) * Rot(0, 90, 0) * Cylinder(inlet_radius, inlet_length)
solid_body = solid_body + inlet

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(mount_hole_count):
    x = (i - (mount_hole_count - 1) / 2) * mount_hole_spacing
    hole = Pos(x, 0, length/2) * Cylinder(mount_hole_diameter/2, length + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_inlet"
export_step(part, "output.step")