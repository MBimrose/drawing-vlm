from build123d import *
import math

base_radius = 8.0
vertical_height = 60.0
horizontal_extension = 30.0
horizontal_thickness = 20.0
chamfer_val = 1.0
tube_outer_diameter = 12.0
tube_inner_diameter = 8.0
tube_length = 15.0
hole_circle_radius = 20.0
blind_hole_diameter = 5.0
blind_hole_depth = 10.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, vertical_height))
            l3 = Line(l2 @ 1, (base_radius + horizontal_extension, vertical_height))
            l4 = Line(l3 @ 1, (base_radius + horizontal_extension, vertical_height + horizontal_thickness))
            l5 = Line(l4 @ 1, (0, vertical_height + horizontal_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_val)

tube_cx = base_radius + horizontal_extension / 2
tube_cy = vertical_height + horizontal_thickness / 2
outer_cyl = Pos(tube_cx, tube_cy, 0) * Rot(0, 90, 0) * Cylinder(tube_outer_diameter / 2, tube_length)
inner_cyl = Pos(tube_cx, tube_cy, 0) * Rot(0, 90, 0) * Cylinder(tube_inner_diameter / 2, tube_length)
solid_body = solid_body - (outer_cyl - inner_cyl)

top_z = vertical_height + horizontal_thickness
for i in range(4):
    a = math.radians(i * 360.0 / 4)
    px = hole_circle_radius * math.cos(a)
    py = hole_circle_radius * math.sin(a)
    solid_body = solid_body - Pos(px, py, top_z - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)

part = solid_body
part.name = "L_Mount_Revolve"
export_step(part, OUTPUT_PATH)