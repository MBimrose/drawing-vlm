from build123d import *

base_radius = 15.0
base_height = 15.0
mid_radius = 25.0
mid_height = 30.0
top_radius = 10.0
total_height = 80.0
bore_radius = 5.0
counterbore_radius = 8.0
counterbore_depth = 10.0
chamfer_base = 1.5
chamfer_top = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_radius, 0), (base_radius, base_height),
                     (mid_radius, base_height + mid_height),
                     (top_radius, total_height), (0, total_height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(bore_radius, total_height + 2)
solid_body = solid_body - Pos(0, 0, counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_base)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_top)

part = solid_body
part.name = "revolved_profile_with_holes"
export_step(part, "output.step")