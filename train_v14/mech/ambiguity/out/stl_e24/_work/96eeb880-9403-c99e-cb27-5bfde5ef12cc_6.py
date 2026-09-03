from build123d import *

block_length = 80
block_width = 50
block_thickness = 12
corner_radius = 8
chamfer_distance = 5
hole_diameter = 6
hole_spacing = 25
rib_height = 10
rib_width = 6
rib_spacing = 20

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-block_length/2, -block_width/2), (block_length/2, -block_width/2))
            l2 = Line(l1@1, (block_length/2, block_width/2 - corner_radius))
            a1 = RadiusArc(l2@1, (block_length/2 - corner_radius, block_width/2), corner_radius)
            l3 = Line(a1@1, (-block_length/2, block_width/2))
            l4 = Line(l3@1, (-block_length/2, -block_width/2))
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + 1)

rib_count = int((block_length - 2*corner_radius) // rib_spacing)
for i in range(rib_count):
    x_pos = -block_length/2 + corner_radius + rib_spacing/2 + i*rib_spacing
    rib = Pos(x_pos, 0, -rib_height/2) * Box(rib_width, block_thickness - 2, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "block_with_ribs"
export_step(part, "output.step")