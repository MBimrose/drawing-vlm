from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
dovetail_depth = 15.0
dovetail_top_width = 20.0
dovetail_bottom_width = 40.0
fillet_radius = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_width = 5.0
rib_height = 4.0
rib_spacing = 15.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as dovetail:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            Polyline((-dovetail_bottom_width/2, -outer_width/2),
                     (-dovetail_top_width/2, outer_width/2),
                     (dovetail_top_width/2, outer_width/2),
                     (dovetail_bottom_width/2, -outer_width/2),
                     close=True)
        make_face()
    extrude(amount=dovetail_depth)
base = base - dovetail.part

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    base = base - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

rib_count = int((outer_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = -outer_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    base = base + Pos(x, 0, outer_height + wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)

part = base
part.name = "dovetail_box"
export_step(part, "output.step")