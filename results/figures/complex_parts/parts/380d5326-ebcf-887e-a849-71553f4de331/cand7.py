from build123d import *

total_length = 80.0
start_diameter = 20.0
end_diameter = 28.0
wall_thickness = 2.0
boss_diameter = 12.0
boss_height = 20.0
boss_offset = 30.0
hole_diameter = 4.0
chamfer_distance = 1.0

start_radius = start_diameter / 2.0
end_radius = end_diameter / 2.0
boss_radius = boss_diameter / 2.0
inner_start_radius = start_radius - wall_thickness
inner_end_radius = end_radius - wall_thickness

with BuildPart() as p_outer:
    with BuildSketch() as s1:
        Circle(start_radius)
    with BuildSketch(Plane.XY.offset(total_length)) as s2:
        Circle(end_radius)
    loft()
outer = p_outer.part

with BuildPart() as p_inner:
    with BuildSketch() as s3:
        Circle(inner_start_radius)
    with BuildSketch(Plane.XY.offset(total_length)) as s4:
        Circle(inner_end_radius)
    loft()
inner = p_inner.part

shell = outer - inner

boss = Pos(boss_offset, 0, total_length / 2.0) * Cylinder(boss_radius, boss_height)
combined = shell + boss

hole = Pos(boss_offset, 0, total_length / 2.0) * Cylinder(hole_diameter / 2.0, boss_height + 2.0)
combined = combined - hole

combined = chamfer(combined.edges(), chamfer_distance)

part = combined
part.name = "lofted_shell_with_boss"
export_step(part, "output.step")