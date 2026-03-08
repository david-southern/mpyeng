include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <../useful-stuff.scad>
include <../audio-jack-collar.scad>
include <../seven-seg-collar.scad>
include <right-panel-constants.scad>

/* [Hidden] */

/* [Rendering Options] */
RenderPieces = 254; // [1: Panel Mock, 2: Card Tray, 128: LED Mock, 254: NoPanel, 255: All]
lo_rez_mocks = false;
optix_thickness = 3.175;

/* [Card Tray Options] */
card_tray_brim = 5; // 0.1
card_tray_base_thickness = 3; // 0.1
card_tray_inner_rounding = 4; // 0.1

card_tray_bracket_height = 10; // 0.1
card_tray_bracket_depth = 15; // 0.1
card_tray_bracket_offset = 5; // 0.1

inner_tray_flush_with_panel = true;
inner_tray_cutout = false;

magnet_hole_wall_thickness = 2; // 0.1

/* [Hidden] */
card_tray_size = led_grid_size + card_tray_brim * 2;
card_tray_thickness = card_tray_base_thickness + pixel_thickness + optix_thickness;

power_card_width = card_tray_size;
power_card_height = card_tray_size + card_tray_bracket_height * 2 + card_tray_bracket_offset * 2;
power_card_depth = max(card_tray_thickness, card_tray_bracket_depth);

card_bay_width = power_card_width;
card_bay_height = power_card_height;
card_bay_depth = power_card_depth;

magnet_hole_inner_diameter = magnet_diameter + printer_fudge;
magnet_hole_outer_diameter = magnet_hole_inner_diameter + magnet_hole_wall_thickness * 2;

card_tray_outer_rounding = magnet_hole_outer_diameter / 2;

if (CheckRenderPieces(PIECES_PANEL)) {
    render()
        panel_base(anchor=TOP);
}

if (CheckRenderPieces(PIECES_CARD_TRAY)) {
    render() {
        card_tray(anchor=BOTTOM);
    }
}

if (CheckRenderPieces(PIECES_LED_MOCK)) {
    render() {
        led_mock_offset = CheckRenderPieces(PIECES_CARD_TRAY) ? card_tray_base_thickness : 0;
        echo(str("LED Mock Offset: ", led_mock_offset));

        up(led_mock_offset)
            led_mock(anchor=BOTTOM);
    }
}

module card_tray(anchor = CENTER, spin = 0, orient = UP) {
    card_tray_width = card_tray_size;
    card_tray_height = card_tray_size + card_tray_bracket_height * 2 + card_tray_bracket_offset * 2;
    card_tray_depth = card_tray_bracket_depth;

    attachable(anchor, spin, orient, size=[card_tray_width, card_tray_height, card_tray_depth]) {
        union() {
            down(card_tray_bracket_depth / 2)
                inner_card_tray(anchor=BOTTOM) {
                    color("pink") {
                        position(FRONT + BOTTOM)
                            fwd(card_tray_bracket_offset)
                                cuboid(
                                    [
                                        card_tray_size,
                                        card_tray_bracket_height,
                                        card_tray_bracket_depth,
                                    ],
                                    rounding=4,
                                    edges="Z",
                                    anchor=BACK + BOTTOM
                                );

                        position(BACK + BOTTOM)
                            back(card_tray_bracket_offset)
                                cuboid(
                                    [
                                        card_tray_size,
                                        card_tray_bracket_height,
                                        card_tray_bracket_depth,
                                    ],
                                    rounding=4,
                                    edges="Z",
                                    anchor=FRONT + BOTTOM
                                );
                    }
                }
        }
        children();
    }
}

module inner_card_tray(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[card_tray_size, card_tray_size, card_tray_thickness]) {
        if (lo_rez_mocks) {
            color("mediumseagreen")
                cuboid(
                    [
                        card_tray_size,
                        card_tray_size,
                        card_tray_thickness,
                    ],
                    rounding=card_tray_outer_rounding,
                    edges="Z",
                    anchor=CENTER
                );
        } else {
            down(card_tray_thickness / 2) {
                recolor("mediumseagreen") {
                    diff(remove="inner_cutout solder_cutout") {
                        cuboid(
                            [
                                card_tray_size,
                                card_tray_size,
                                card_tray_thickness,
                            ],
                            rounding=card_tray_outer_rounding,
                            edges="Z",
                            anchor=BOTTOM
                        ) {
                            position(TOP)

                                xcopies(l=card_tray_size - magnet_hole_outer_diameter, n=2) {
                                    ycopies(l=card_tray_size - magnet_hole_outer_diameter, n=2) {
                                        cyl(
                                            d=magnet_hole_outer_diameter,
                                            h=optix_thickness + epsilon,
                                            anchor=TOP
                                        );
                                    }
                                }

                            position(BOTTOM) {
                                tag("inner_cutout") {
                                    up(card_tray_base_thickness + pixel_thickness) {
                                        cuboid(
                                            [
                                                led_grid_size,
                                                led_grid_size,
                                                optix_thickness + epsilon,
                                            ],
                                            rounding=card_tray_inner_rounding,
                                            edges="Z",
                                            anchor=BOTTOM
                                        );

                                        if (inner_tray_cutout) {
                                            cuboid(
                                                [
                                                    led_grid_size * 0.67,
                                                    card_tray_size,
                                                    optix_thickness + epsilon,
                                                ],
                                                rounding=-optix_thickness,
                                                edges=[TOP],
                                                anchor=BOTTOM
                                            );

                                            cuboid(
                                                [
                                                    card_tray_size,
                                                    led_grid_size * 0.67,
                                                    optix_thickness + epsilon,
                                                ],
                                                rounding=-optix_thickness,
                                                edges=[TOP],
                                                anchor=BOTTOM
                                            );
                                        }
                                    }

                                    up(card_tray_base_thickness)
                                        cuboid(
                                            [
                                                led_grid_size,
                                                led_grid_size,
                                                pixel_thickness,
                                            ],
                                            anchor=BOTTOM
                                        );
                                }

                                // Mock card acrylic size
                                *recolor("#dddddd")
                                    up(card_tray_base_thickness + pixel_thickness + optix_thickness)
                                        cuboid(
                                            [
                                                card_tray_size,
                                                card_tray_size + 10,
                                                optix_thickness,
                                            ],
                                            rounding=card_tray_inner_rounding,
                                            edges="Z",
                                            anchor=BOTTOM
                                        );
                            }

                            position(BOTTOM + RIGHT)
                                tag("solder_cutout") {
                                    left(led_grid_solder_pads_offset_right + card_tray_brim)
                                        cuboid(
                                            [
                                                led_grid_solder_pads_width,
                                                led_grid_solder_pads_height,
                                                card_tray_base_thickness * 2,
                                            ],
                                            anchor=BOTTOM + RIGHT
                                        );
                                }
                        }
                    }
                }
            }
        }

        children();
    }
}

module led_mock(anchor = CENTER, spin = 0, orient = UP) {
    mock_thickness = led_grid_thickness + optix_thickness;
    attachable(anchor, spin, orient, size=[led_grid_size, led_grid_size, mock_thickness]) {
        down(mock_thickness / 2)
            union() {
                recolor("#555555")
                    cuboid(
                        [
                            led_grid_size,
                            led_grid_size,
                            0.1,
                        ],
                        anchor=BOTTOM
                    ) {
                        position(BOTTOM + RIGHT)
                            recolor("cyan")
                                left(led_grid_solder_pads_offset_right)
                                    cuboid(
                                        [
                                            led_grid_solder_pads_width,
                                            led_grid_solder_pads_height,
                                            1,
                                        ],
                                        anchor=TOP + RIGHT
                                    );

                        position(TOP) {
                            xcopies(l=led_grid_size - 10, n=8) {
                                xidx = $idx;
                                ycopies(l=led_grid_size - 10, n=8) {
                                    yidx = $idx;
                                    recolor("white")
                                        cuboid(
                                            [
                                                pixel_size,
                                                pixel_size,
                                                pixel_thickness,
                                            ],
                                            anchor=BOTTOM
                                        );
                                }
                            }
                        }
                    }

                // Mock optix acrylic over the LEDS
                *up(pixel_thickness)
                    %cuboid(
                        [
                            led_grid_size,
                            led_grid_size,
                            optix_thickness,
                        ],
                        rounding=card_tray_inner_rounding,
                        edges="Z",
                        anchor=BOTTOM
                    );
            }

        children();
    }
}

module panel_base(anchor = CENTER, spin = 0, orient = UP) {
    attachable(anchor, spin, orient, size=[eng_panel_width, eng_panel_height, eng_panel_thickness]) {
        color("burlywood")
            cuboid(
                [
                    card_bay_width * 3,
                    card_bay_height * 3,
                    eng_panel_thickness,
                ],
                anchor=CENTER
            );
        children();
    }
}
