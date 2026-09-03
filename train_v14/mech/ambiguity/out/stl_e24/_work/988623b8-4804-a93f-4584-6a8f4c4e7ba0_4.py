from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
mount_hole_dia = 4.0
mount_hole_offset = 5.0
rib_width = 12.0
rib_height = 4.0
rib_spacing = 20.0
rib_depth = 2.0
gusset_thickness = 4.0
gusset_height = 20.0
gusset_width = 20.0
countersink_dia = 5.0
countersink_angle = 82.0
countersink_depth = 2.0

result = Box(plate_length, plate_width, plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness * 2)

rib_count = int((plate_length - 2*mount_hole_offset) // rib_spacing) + 1
rib_start = -plate_length/2 + mount_hole_offset
for i in range(rib_count):
    x = rib_start + i * rib_spacing
    result = result - Pos(x, 0, -plate_thickness/2 + rib_depth/2) * Box(rib_width, rib_height, rib_depth)

with BuildPart() as gusset_bp:
    with BuildSketch(Plane.YZ.offset(plate_length/2)) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (gusset_width, 0), (gusset_width/2, gusset_height), close=True)
        make_face()
    extrude(amount=gusset_thickness)
result = result + gusset_bp.part

csk_radius = countersink_dia / 2
csk_sink_radius = csk_radius + countersink_depth * math.tan(math.radians(countersink_angle / 2))
result = result - Pos(0, 0, plate_thickness/2) * CounterSinkHole(csk_radius, csk_sink_radius, countersink_depth, countersink_angle)

part = result
part.name = "plate_with_gusset"
export_step(part, "output.step")