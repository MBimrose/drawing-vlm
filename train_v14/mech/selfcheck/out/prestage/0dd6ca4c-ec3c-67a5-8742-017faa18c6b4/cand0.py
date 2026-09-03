from build123d import *

base_diameter = 30.0
base_length = 15.0
taper_length = 30.0
top_diameter = 20.0
top_length = 35.0
bore_diameter = 10.0
countersink_diameter = 16.0
countersink_depth = 5.0
chamfer_size = 1.0

base_radius = base_diameter / 2.0
top_radius = top_diameter / 2.0
bore_radius = bore_diameter / 2.0
countersink_radius = countersink_diameter / 2.0
total_length = base_length + taper_length + top_length

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (base_radius, base_length))
            l3 = Line(l2 @ 1, (base_radius + 10, base_length + taper_length))
            l4 = Line(l3 @ 1, (top_radius, total_length))
            l5 = Line(l4 @ 1, (0, total_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_radius, total_length + 10)
solid_body = solid_body - Pos(0, 0, total_length - countersink_depth / 2) * Cone(bore_radius, countersink_radius, countersink_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_profile_with_bore"
export_step(part, "output.step")