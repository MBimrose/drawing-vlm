from build123d import *

rod_length = 60.0
rod_radius = 5.0
wall_thickness = 2.0
inner_radius = rod_radius - wall_thickness
tab_width = 12.0
tab_height = 8.0
tab_thickness = 4.0
pocket_width = 6.0
pocket_height = 4.0
pocket_depth = 2.0
pocket_offset = 30.0

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (rod_length, 0), (rod_length, rod_radius), (0, rod_radius), close=True)
        make_face()
    revolve(axis=Axis.X)

solid_body = p.part
solid_body = solid_body - Pos(rod_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(inner_radius, rod_length + 10)
solid_body = solid_body + Pos(rod_length, 0, 0) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body - Pos(pocket_offset, 0, 0) * Box(pocket_width, pocket_depth, pocket_height)

part = solid_body
part.name = "rod_with_tab_and_pocket"
export_step(part, "output.step")