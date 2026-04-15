include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <../useful-stuff.scad>
include <../audio-jack-collar.scad>
include <../seven-seg-collar.scad>
include <right-panel-constants.scad>

/* [Hidden] */
$fn = 37;
PIECES_FACE = 1;
PIECES_WALLS = 2;
PIECES_BUMPS = 4;
PIECES_ALL = 255;

optix_thickness = 3.175;
pixel_size = 5;
grid_cell_size = 10;

/* [Render Options] */
RenderPieces = 255; // [1: Face, 2: Walls, 4:Bumps, 255: All]
stepped_face_thicknesses = false; // [true, false]
grid_bumps = true; // [true, false]

/* [Printer Options] */
printer_layer_height = 0.24; // [0.08, 0.12, 0.16, 0.20, 0.24]
printer_line_width = 0.42; // [0.21, 0.42, 0.63]

/* [Grid Options] */
grid_size = 8; // [8, 16]

nominal_grid_wall_thickness = 0.25;
nominal_grid_face_thickness = 0.25;
grid_wall_depth = 4;
nominal_grid_bump_depth = 1.5;

/* [Hidden] */
grid_dimension = grid_size * grid_cell_size;
grid_wall_thickness = max(floor(nominal_grid_wall_thickness / printer_line_width), 1) * printer_line_width;
grid_face_thickness = max(floor(nominal_grid_face_thickness / printer_layer_height), 1) * printer_layer_height;
grid_bump_depth = max(floor(nominal_grid_bump_depth / printer_layer_height), 1) * printer_layer_height;

echo(
    str(
        "Generating Grid with wall: ", grid_wall_thickness,
        ", face: ", grid_face_thickness
    )
);

render() {
    if (CheckRenderPieces(PIECES_FACE)) {
        grid_face(anchor=TOP){}
    }

    if (CheckRenderPieces(PIECES_WALLS)) {
        grid_walls(anchor=BOTTOM);
    }

    if (CheckRenderPieces(PIECES_BUMPS) && grid_bumps) {
        grid_bumps(anchor=BOTTOM);
    }
}

module grid_face(anchor = CENTER, spin = 0, orient = UP) {
    grid_face_width = grid_dimension;
    grid_face_height = grid_dimension;
    grid_face_depth = grid_face_thickness;

    attachable(anchor, spin, orient, size=[grid_face_width, grid_face_height, grid_face_depth]) {
        if (stepped_face_thicknesses) {
            down(grid_face_depth / 2) {
                color("red")
                    cuboid(
                        [
                            grid_face_width / 2,
                            grid_face_height / 2,
                            grid_face_depth,
                        ],
                        anchor=FRONT + RIGHT + BOTTOM
                    );
                color("green")
                    cuboid(
                        [
                            grid_face_width / 2,
                            grid_face_height / 2,
                            grid_face_depth * 2,
                        ],
                        anchor=FRONT + LEFT + BOTTOM
                    );
                color("blue")
                    cuboid(
                        [
                            grid_face_width / 2,
                            grid_face_height / 2,
                            grid_face_depth * 3,
                        ],
                        anchor=BACK + RIGHT + BOTTOM
                    );
                color("yellow")
                    cuboid(
                        [
                            grid_face_width / 2,
                            grid_face_height / 2,
                            grid_face_depth * 4,
                        ],
                        anchor=BACK + LEFT + BOTTOM
                    );
            }
            ;
        } else {
            cuboid(
                [
                    grid_face_width,
                    grid_face_height,
                    grid_face_depth,
                ],
                anchor=CENTER
            );
        }

        children();
    }
}

module grid_walls(anchor = CENTER, spin = 0, orient = UP) {
    grid_walls_width = grid_dimension;
    grid_walls_height = grid_dimension;
    grid_walls_depth = grid_wall_depth;

    attachable(anchor, spin, orient, size=[grid_walls_width, grid_walls_height, grid_walls_depth]) {
        union() {
            xcopies(spacing=grid_cell_size, n=grid_size - 1)
                cuboid(
                    [
                        grid_wall_thickness,
                        grid_walls_height,
                        grid_walls_depth,
                    ],
                    anchor=CENTER
                );

            ycopies(spacing=grid_cell_size, n=grid_size - 1)
                cuboid(
                    [
                        grid_walls_width,
                        grid_wall_thickness,
                        grid_walls_depth,
                    ],
                    anchor=CENTER
                );
        }

        children();
    }
}

max_chord_length = grid_cell_size - grid_wall_thickness;

module bump(bump_sagitta, chord_pct, anchor = CENTER, spin = 0, orient = UP) {
    bump_chord_length = max_chord_length * chord_pct;
    bump_radius = bump_chord_length ^ 2 / (8 * bump_sagitta) + bump_sagitta / 2;

    echo(
        str(
            "Bump with sagitta: ", bump_sagitta,
            ", radius: ", bump_radius
        )
    );

    attachable(anchor, spin, orient, size=[bump_chord_length, bump_chord_length, bump_sagitta]) {
        down(bump_radius - bump_sagitta / 2)
            difference() {
                spheroid(r=bump_radius, style="octa");
                down(bump_sagitta)
                    cuboid(
                        [
                            bump_radius * 2,
                            bump_radius * 2,
                            bump_radius * 2,
                        ]
                    );
            }

        children();
    }
}

module grid_bumps(anchor = CENTER, spin = 0, orient = UP) {
    grid_bumps_width = grid_dimension;
    grid_bumps_height = grid_dimension;
    grid_bumps_depth = grid_bump_depth;

    attachable(anchor, spin, orient, size=[grid_bumps_width, grid_bumps_height, grid_bumps_depth]) {
        down(grid_bumps_depth / 2)
            grid_copies(spacing=grid_cell_size, n=grid_size)
                bump(
                    max(printer_layer_height, grid_bump_depth * $row / (grid_size - 1)),
                    0.5 + $col / (grid_size - 1) / 2,
                    anchor, spin, orient
                );

        children();
    }
}
