from build123d import *

bracket_length = 70.0
bracket_width = 30.0
bracket_thickness = 8.0
gusset_width = 10.0
gusset_height = 6.0
gusset_offset = 15.0
pocket_length = 20.0
pocket_width = 6.0
pocket_depth = 4.0
hole_diameter = 8.0
hole_offset_x = 20.0
hole_offset_y = 0.0
fillet_radius = 1.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-gusset_width/2, 0), (gusset_width/2, 0), (0, gusset_height), close=True)
        make_face()
    extrude(amount=bracket_thickness)
gusset = Pos(gusset_offset, bracket_width/2, 0) * gp.part

result = base + gusset

pocket = Pos(0, bracket_width/2 - pocket_depth/2, 0) * Box(pocket_length, pocket_depth, pocket_width)
result = result - pocket

hole = Pos(hole_offset_x, hole_offset_y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 10)
result = result - hole

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bracket"
export_step(part, "output.step")