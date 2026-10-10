from build123d import *

total_length = 80.0
base_radius = 8.0
top_radius = 12.0
tube_wall = 2.0
bush_length = 20.0
bush_outer_radius = 6.0
bush_inner_radius = 4.0
bush_offset = 15.0
mount_hole_dia = 4.0
chamfer_dist = 1.0

with BuildPart() as outer:
    with BuildSketch() as s1:
        Circle(base_radius + tube_wall)
    with BuildSketch(Plane.XY.offset(total_length)) as s2:
        Circle(top_radius + tube_wall)
    loft()

outer_shell = outer.part
outer_shell = chamfer(outer_shell.edges(), chamfer_dist)

with BuildPart() as inner:
    with BuildSketch() as s3:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(total_length)) as s4:
        Circle(top_radius)
    loft()

inner_cavity = inner.part

tube = outer_shell - inner_cavity
tube = tube - Pos(0, 0, total_length/2) * Cylinder(mount_hole_dia/2, total_length * 2)

bush = Pos(bush_offset, 0, total_length/2) * Cylinder(bush_outer_radius, bush_length)
bush = bush - Pos(bush_offset, 0, total_length/2) * Cylinder(bush_inner_radius/2, bush_length)
bush = chamfer(bush.edges(), chamfer_dist)

part = tube + bush
part.name = "lofted_tube_with_bush"
export_step(part, OUTPUT_PATH)