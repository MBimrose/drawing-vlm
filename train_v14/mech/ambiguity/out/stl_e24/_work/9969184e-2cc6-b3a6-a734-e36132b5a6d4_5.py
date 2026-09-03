from build123d import *
import math

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
groove_width = 4.0
groove_depth = 2.0
groove_pitch = 12.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 30.0
keyway_chamfer = 0.8
mount_hole_diameter = 6.0
mount_hole_offset = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (inner_radius, length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    z = t * length
    angle = t * (length / groove_pitch) * 2 * math.pi
    r = outer_radius - groove_depth / 2.0
    helix_pts.append(Vector(r * math.cos(angle), r * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_path = bl.wire()

with BuildSketch(Plane.XZ) as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch

groove_solid = sweep(sections=groove_face, path=helix_path)
solid_body = solid_body - groove_solid

keyway_box = Pos(outer_radius - keyway_depth / 2.0, 0, length / 2.0) * Box(keyway_depth, keyway_width, keyway_length)
keyway_box = chamfer(keyway_box.edges(), keyway_chamfer)
solid_body = solid_body - keyway_box

mount_hole = Pos(mount_hole_offset, 0, 0) * Cylinder(mount_hole_diameter / 2.0, length)
solid_body = solid_body - mount_hole

part = solid_body
part.name = "hollow_shaft_with_groove_keyway"
export_step(part, "output.step")