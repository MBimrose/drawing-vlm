from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
gusset_height = 6.0
gusset_base = 10.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 0.0
fillet_radius = 1.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 4.0
pocket_offset_x = 0.0
pocket_offset_y = 5.0

base = Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as g:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-gusset_base/2, -bracket_thickness/2), (gusset_base/2, -bracket_thickness/2), (0, -bracket_thickness/2 + gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
gusset = Pos(0, bracket_width/2, 0) * g.part

result = base + gusset
result = result - Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)
result = result - Pos(pocket_offset_x, pocket_offset_y, bracket_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket_with_gusset"
export_step(part, "output.step")