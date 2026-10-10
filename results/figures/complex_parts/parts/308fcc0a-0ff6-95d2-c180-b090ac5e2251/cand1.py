from build123d import *

base_radius = 30.0
top_radius = 40.0
height = 40.0
wall_thickness = 5.0
fillet_radius = 2.0
hole_diameter = 10.0
hole_offset = 20.0

with BuildPart() as p_outer:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(height)) as s2:
        Circle(top_radius)
    loft()
outer = p_outer.part

with BuildPart() as p_inner:
    with BuildSketch() as s3:
        Circle(base_radius - wall_thickness)
    with BuildSketch(Plane.XY.offset(height)) as s4:
        Circle(top_radius - wall_thickness)
    loft()
inner = p_inner.part

solid_body = outer - inner
solid_body = fillet(solid_body.edges(), fillet_radius)
solid_body = solid_body - Pos(hole_offset, height/2, height/2) * Cylinder(hole_diameter/2, height)

part = solid_body
part.name = "lofted_shell_with_hole"
export_step(part, "output.step")