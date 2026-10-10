from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 8.0
cyl_radius = 20.0
cyl_height = 25.0
cone_height = 27.0
cone_tip_radius = 5.0
mount_hole_dia = 6.0
mount_hole_offset_x = 30.0
mount_hole_offset_y = 15.0
chamfer_size = 1.0

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (cyl_radius, 0))
            l2 = Line(l1 @ 1, (cyl_radius, cyl_height))
            l3 = Line(l2 @ 1, (cone_tip_radius, cyl_height + cone_height))
            l4 = Line(l3 @ 1, (0, cyl_height + cone_height))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

nozzle = Pos(0, 0, base_thickness) * p.part
result = base + nozzle

hole_positions = [
    (mount_hole_offset_x, mount_hole_offset_y),
    (-mount_hole_offset_x, mount_hole_offset_y),
    (mount_hole_offset_x, -mount_hole_offset_y),
    (-mount_hole_offset_x, -mount_hole_offset_y),
]

for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness / 2) * Cylinder(mount_hole_dia / 2, base_thickness + 2)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "nozzle_base"
export_step(part, "output.step")