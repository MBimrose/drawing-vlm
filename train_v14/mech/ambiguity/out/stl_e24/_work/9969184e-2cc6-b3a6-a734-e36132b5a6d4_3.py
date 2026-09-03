from build123d import *
import math

outer_diameter = 40.0
inner_diameter = 20.0
length = 80.0
groove_width = 4.0
groove_depth = 2.0
groove_pitch = 10.0
hole_diameter = 6.0
hole_offset = 12.0
slot_width = 8.0
slot_depth = 4.0
slot_offset = 30.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

helix_radius = inner_radius + groove_depth / 2.0
num_pts = 200
helix_pts = []
for i in range(num_pts):
    t = i / (num_pts - 1)
    angle = 2 * math.pi * length / groove_pitch * t
    z = length * t
    helix_pts.append(Vector(helix_radius * math.cos(angle), helix_radius * math.sin(angle), z))

with BuildLine() as bl:
    Spline(*helix_pts)
helix_wire = bl.wire()

with BuildSketch() as gs:
    Rectangle(groove_width, groove_depth)
groove_face = gs.sketch.faces()[0]

groove_solid = sweep(sections=groove_face, path=helix_wire)
result = result - groove_solid

result = result - Pos(hole_offset, 0, -length/2) * Cylinder(hole_diameter/2, length)

slot_box = Pos(outer_radius - wall_thickness/2, 0, slot_offset - length/2) * Box(slot_width, slot_depth, wall_thickness)
result = result - slot_box

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_groove"
export_step(part, "output.step")