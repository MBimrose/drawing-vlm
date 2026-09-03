from build123d import *

channel_length = 90.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 3.0
slot_width = 10.0
slot_length = 30.0
fillet_radius = 2.0
rib_height = 12.0
rib_thickness = 4.0
mount_hole_diameter = 5.0
mount_hole_spacing = 20.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

slot = Pos(0, 0, channel_height - wall_thickness/2) * Box(slot_length, slot_width, wall_thickness)
base = base - slot

bottom_edges = base.edges().sort_by(Axis.Z)[:4]
base = fillet(bottom_edges, fillet_radius)

with BuildPart() as rib_bp:
    with BuildSketch(Plane.XZ.offset(-channel_width/2)) as sk:
        RegularPolygon(rib_height/2, 3)
    extrude(amount=rib_thickness)
base = base + rib_bp.part

for x, y in [(-channel_length/2 + mount_hole_spacing, 0), (-channel_length/2 + 2*mount_hole_spacing, 0)]:
    hole = Pos(x, -channel_width/2, channel_height) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, channel_width)
    base = base - hole

part = base
part.name = "channel_with_rib"
export_step(part, "output.step")