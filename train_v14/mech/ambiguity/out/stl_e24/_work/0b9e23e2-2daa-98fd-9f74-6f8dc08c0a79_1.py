from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
cavity_length = 40.0
cavity_width = 20.0
cavity_depth = 20.0
cavity_radius = 5.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
rib_thickness = 5.0
rib_height = 10.0
rib_spacing = 20.0
chamfer_size = 1.0

solid_body = Box(block_length, block_width, block_height)

with BuildPart() as cavity_bp:
    with BuildSketch(Plane.XY.offset(block_height/2)) as cavity_sk:
        with BuildLine() as cavity_line:
            l1 = Line((-cavity_length/2, 0), (-cavity_length/2, cavity_width - cavity_radius))
            a1 = ThreePointArc(l1@1, (-cavity_length/2 + cavity_radius, cavity_width), (0, cavity_width))
            a2 = ThreePointArc(a1@1, (cavity_length/2 - cavity_radius, cavity_width), (cavity_length/2, cavity_width - cavity_radius))
            l2 = Line(a2@1, (cavity_length/2, 0))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-cavity_depth)

solid_body = solid_body - cavity_bp.part

cbore = Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

thru = Pos(0, 0, 0) * Cylinder(through_hole_diameter/2, block_height + 10)
solid_body = solid_body - thru

mount_points = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

rib_count = int((block_height - 2*mount_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    z_pos = -block_height/2 + mount_hole_offset + i * rib_spacing
    rib = Pos(0, block_width/2 - rib_thickness/2, z_pos) * Box(block_length, rib_thickness, rib_thickness)
    solid_body = solid_body - rib

y_face = solid_body.faces().sort_by(Axis.Y)[-1]
y_edges = y_face.edges().filter_by(Axis.Z)
solid_body = chamfer(y_edges, chamfer_size)

part = solid_body
part.name = "block_with_cavity_and_ribs"
export_step(part, "output.step")