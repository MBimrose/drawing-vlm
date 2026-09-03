from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
cavity_width = 30.0
cavity_depth = 20.0
cavity_radius = 10.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
chamfer_size = 1.0
rib_thickness = 5.0
rib_height = 10.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

with BuildPart() as cavity_bp:
    with BuildSketch(Plane.XY.offset(block_height)) as sk:
        with BuildLine() as bl:
            l1 = Line((-cavity_width/2, 0), (-cavity_width/2, cavity_depth - cavity_radius))
            a1 = ThreePointArc(l1@1, (0, cavity_depth), (cavity_width/2, cavity_depth - cavity_radius))
            l2 = Line(a1@1, (cavity_width/2, 0))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-cavity_depth)
cavity_solid = cavity_bp.part

result = base - cavity_solid

cbore = Pos(0, cavity_depth/2, block_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - cbore

thru = Pos(0, cavity_depth/2, block_height/2) * Cylinder(through_hole_diameter/2, block_height)
result = result - thru

mount_pts = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in mount_pts:
    result = result - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

rib1 = Pos(0, block_width/2 - rib_thickness/2, block_height/4) * Box(block_length, rib_thickness, rib_height)
rib2 = Pos(0, block_width/2 - rib_thickness/2, 3*block_height/4) * Box(block_length, rib_thickness, rib_height)
result = result - rib1 - rib2

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_cavity_and_ribs"
export_step(part, "output.step")