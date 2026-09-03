from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 8.0
depth = 12.0
gusset_width = 20.0
gusset_height = 20.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset_from_bottom = 20.0
chamfer_size = 3.0
pocket_diameter = 20.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length + thickness, 0))
            l2 = Line(l1@1, (leg_length + thickness, thickness))
            l3 = Line(l2@1, (thickness, thickness))
            l4 = Line(l3@1, (thickness, leg_height))
            l5 = Line(l4@1, (0, leg_height))
            l6 = Line(l5@1, (0, 0))
        make_face()
    extrude(amount=depth)

solid = p.part
inner_edges = [e for e in solid.edges().filter_by(Axis.Z) if abs(e.center().X - thickness) < 0.5 and abs(e.center().Y - thickness) < 0.5]
solid = chamfer(inner_edges, chamfer_size)

with BuildPart() as g:
    with BuildSketch() as gsk:
        with BuildLine() as gbl:
            gl1 = Line((thickness, thickness), (thickness + gusset_width, thickness))
            gl2 = Line(gl1@1, (thickness, thickness + gusset_height))
            gl3 = Line(gl2@1, (thickness, thickness))
        make_face()
    extrude(amount=depth)

solid = solid + g.part

for i in range(3):
    y = hole_offset_from_bottom + i * hole_spacing
    solid = solid - Pos(thickness/2, y, depth/2) * Cylinder(hole_diameter/2, depth)

solid = solid - Pos(leg_length/2 + thickness/2, thickness/2, depth - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")