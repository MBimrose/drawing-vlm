from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 6.0
rib_count = 5
hole_diameter = 10.0
chamfer_distance = 0.5
stiff_rib_width = 4.0
stiff_rib_length = 15.0
stiff_rib_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(arm_length, arm_width)
    extrude(amount=arm_thickness)

solid_body = p.part

for i in range(rib_count):
    x = -arm_length/2 + rib_spacing + i * rib_spacing
    rib = Pos(x, 0, arm_thickness + rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

stiff_rib = Pos(-arm_length/2 + stiff_rib_offset, 0, -stiff_rib_length/2) * Box(stiff_rib_width, arm_width, stiff_rib_length)
solid_body = solid_body + stiff_rib

solid_body = solid_body - Cylinder(hole_diameter/2, 100)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "ribbed_arm"
export_step(part, "output.step")