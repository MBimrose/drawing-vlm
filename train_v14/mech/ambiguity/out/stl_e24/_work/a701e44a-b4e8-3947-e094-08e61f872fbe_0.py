from build123d import *

base_length = 60.0
base_width = 20.0
vertical_height = 40.0
vertical_width = 8.0
thickness = 8.0
fillet_radius = 4.0
hole_diameter = 6.0
cbore_diameter = 10.0
cbore_depth = 5.0
rib_width = 6.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (base_length, 0), (base_length, base_width),
                     (base_length - vertical_width, base_width),
                     (base_length - vertical_width, base_width + vertical_height),
                     (base_length - 2 * vertical_width, base_width + vertical_height),
                     (base_length - 2 * vertical_width, base_width),
                     (0, base_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

fillet_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = fillet(fillet_edges, fillet_radius)

hole_x = base_length - vertical_width / 2
hole_y = base_width + vertical_height / 2
solid_body = solid_body - Pos(hole_x, hole_y, thickness) * CounterBoreHole(hole_diameter/2, cbore_diameter/2, cbore_depth, thickness)

rib_count = int((base_length - 2 * vertical_width) // rib_spacing)
for i in range(rib_count):
    rib_x = vertical_width + rib_spacing / 2 + i * rib_spacing
    rib = Pos(rib_x, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")