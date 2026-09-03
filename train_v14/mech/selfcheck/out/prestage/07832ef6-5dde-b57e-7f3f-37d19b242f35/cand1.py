from build123d import *
import math

stem_radius = 8.0
stem_height = 60.0
head_radius = 38.0
head_height = 20.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0
hole_diameter = 5.0
hole_offset_radius = 20.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (stem_radius, 0), (stem_radius, stem_height),
                     (head_radius, stem_height), (head_radius, stem_height + head_height),
                     (0, stem_height + head_height), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_z = stem_height + head_height

# Pocket cut from top face
solid_body = solid_body - Pos(0, 0, top_z - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

# Four holes in polar array
for i in range(4):
    angle = math.radians(i * 360.0 / 4)
    px = hole_offset_radius * math.cos(angle)
    py = hole_offset_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, top_z - head_height / 2) * Cylinder(hole_diameter / 2, head_height)

# Chamfer top edges
top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "T_profile_with_pocket_and_holes"
export_step(part, "output.step")