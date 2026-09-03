from build123d import *
import math

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
groove_width = 4.0
groove_depth = 2.0
groove_pitch = 20.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_distance = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

base = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    z = t * length
    angle = t * (length / groove_pitch) * 2 * math.pi
    r = inner_radius + groove_depth / 2.0
    helix_pts.append(Vector(r * math.cos(angle), r * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_wire = bl.line

with BuildSketch() as sk:
    Rectangle(groove_width, groove_depth)
profile_face = sk.face()

groove_solid = sweep(sections=profile_face, path=helix_wire)
result = base - groove_solid

hole_cyl = Pos(hole_offset, 0, -length/2) * Cylinder(hole_diameter/2, length)
hole_cyl = chamfer(hole_cyl.edges(), chamfer_distance)
result = result - hole_cyl

part = result
part.name = "helical_groove_sleeve"
export_step(part, "output.step")