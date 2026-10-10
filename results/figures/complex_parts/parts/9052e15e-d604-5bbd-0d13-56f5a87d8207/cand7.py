from build123d import *

horizontal_leg_length = 80.0
vertical_leg_length = 70.0
thickness = 8.0
depth = 20.0
inner_fillet_radius = 2.0
rib_thickness = 3.0
rib_height = 6.0
hole_diameter = 5.0
hole_cbore_diameter = 8.0
hole_cbore_depth = 3.0
hole_spacing = 30.0
hole_offset_from_inner = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (horizontal_leg_length, 0), (horizontal_leg_length, thickness),
                     (thickness, thickness), (thickness, vertical_leg_length + thickness),
                     (0, vertical_leg_length + thickness), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part

inner_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[1:2]
solid_body = fillet(inner_edges, inner_fillet_radius)

rib = Pos(rib_thickness/2, vertical_leg_length + thickness + thickness/2, depth/2) * Box(rib_thickness, thickness, rib_height)
solid_body = solid_body + rib

for i in range(2):
    hx = hole_offset_from_inner + i * hole_spacing
    hy = thickness / 2
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_diameter/2, depth + 1)
    solid_body = solid_body - Pos(hx, hy, 0) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")