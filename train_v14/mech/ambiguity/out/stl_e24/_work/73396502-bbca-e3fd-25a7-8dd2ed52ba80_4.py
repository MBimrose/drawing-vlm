from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 3.3
hole_offset_x = 20.0
hole_offset_y = 12.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 10.0
pocket_depth = 2.0
pocket_width = 20.0
pocket_length = jaw_width - 6.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(jaw_length, jaw_width)
    extrude(amount=jaw_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

pocket = Pos(0, 0, jaw_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-hole_offset_x, -hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 1)

rib_count = int((jaw_length - 2 * rib_spacing) // rib_spacing) + 1
rib_positions = [(-jaw_length/2 + rib_spacing + i * rib_spacing, 0) for i in range(rib_count)]
for x, y in rib_positions:
    rib = Pos(x, y, rib_height/2) * Box(rib_width, jaw_width - 2 * rib_spacing, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "jaw_with_ribs"
export_step(part, "output.step")