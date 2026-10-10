from build123d import *
import math

sprue_height = 50.0
sprue_base_radius = 20.0
sprue_top_radius = 5.0
draft_angle_deg = 30.0
base_plate_length = 80.0
base_plate_width = 50.0
base_plate_thickness = 10.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
fillet_radius = 1.0

draft_angle_rad = math.radians(draft_angle_deg)
radius_diff = sprue_base_radius - sprue_top_radius
vertical_for_draft = radius_diff / math.tan(draft_angle_rad)
if vertical_for_draft > sprue_height:
    vertical_for_draft = sprue_height * 0.5
    sprue_top_radius = sprue_base_radius - math.tan(draft_angle_rad) * vertical_for_draft

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (sprue_base_radius, 0))
            l2 = Line(l1 @ 1, (sprue_base_radius, sprue_height - vertical_for_draft))
            l3 = Line(l2 @ 1, (sprue_top_radius, sprue_height))
            l4 = Line(l3 @ 1, (0, sprue_height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

sprue_cone = p.part
base_plate = Box(base_plate_length, base_plate_width, base_plate_thickness)
sprue_placed = Pos(0, 0, base_plate_thickness / 2) * sprue_cone
combined = base_plate + sprue_placed

bottom_z = -base_plate_thickness / 2
px = (base_plate_length / 2) - mount_hole_offset
py = (base_plate_width / 2) - mount_hole_offset
hole_r = mount_hole_diameter / 2
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    combined = combined - Pos(x, y, bottom_z) * Cylinder(hole_r, 120)

target = Vector(0, 0, base_plate_thickness / 2)
sorted_edges = sorted(combined.edges(), key=lambda e: (e.center() - target).Length)
combined = fillet([sorted_edges[0]], fillet_radius)

part = combined
part.name = "sprue_mold"
export_step(part, OUTPUT_PATH)