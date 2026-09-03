from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
gusset_width = 20.0
gusset_height = 20.0
gusset_thickness = 4.0
mount_hole_dia = 4.0
mount_hole_offset = 5.0
central_hole_dia = 5.0
countersink_dia = 10.0
countersink_angle = 82.0
rib_width = 12.0
rib_depth = 4.0
rib_spacing = 20.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as g:
    with BuildSketch(Plane.YZ.offset(plate_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (gusset_width, 0))
            l2 = Line(l1@1, (gusset_width/2, gusset_height))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=gusset_thickness)

result = base + g.part

corner_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in corner_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness * 2)

result = result - Pos(0, 0, plate_thickness/2) * CounterSinkHole(central_hole_dia/2, countersink_dia/2, plate_thickness, countersink_angle)

num_ribs = int((plate_length - 2*mount_hole_offset) // rib_spacing) + 1
rib_positions = [(-plate_length/2 + mount_hole_offset + i*rib_spacing, 0) for i in range(num_ribs)]
for x, y in rib_positions:
    result = result - Pos(x, y, -plate_thickness/2 + 1.0) * Box(rib_width, rib_depth, 2.0)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "plate_with_gusset"
export_step(part, "output.step")