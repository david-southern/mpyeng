include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <../useful-stuff.scad>
include <../audio-jack-collar.scad>
include <../seven-seg-collar.scad>
include <right-panel-constants.scad>

/* [Hidden] */

/* [Rendering Options] */
RenderPieces = 254; // [1: Panel Mock, 2: Card Tray, 128: LED Mock, 255: All]
separate_for_printing = false;
inner_tray_flush_with_panel = true;
left_split = false;
lo_rez_mocks = false;
mock_optix = false;

/* [Card Tray Options] */
card_tray_brim = 5; // 0.1
card_tray_led_brim = 0.5; // 0.1
card_tray_base_thickness = 3; // 0.1

card_tray_bracket_height = 10; // 0.1
card_tray_bracket_depth = 15; // 0.1
card_tray_bracket_offset = 5; // 0.1

magnet_hole_wall_thickness = 2; // 0.1

/* [Hidden] */
optix_thickness = 3.175;

led_grid_pixels_size = led_grid_size - pixel_size + printer_fudge * 2;

card_tray_size = led_grid_size + card_tray_brim * 2;
card_tray_led_rim = led_grid_pixels_size + card_tray_led_brim * 2;
card_tray_thickness = card_tray_base_thickness + led_grid_thickness + optix_thickness;

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
        if (separate_for_printing) {
            bottom_half(z=card_tray_base_thickness + led_grid_base_thickness * 2 - epsilon)
                inner_card_tray(anchor=BOTTOM);

            up(10)
                top_half(z=card_tray_base_thickness + led_grid_base_thickness * 2 + epsilon)
                    inner_card_tray(anchor=BOTTOM);
        } else {
            if (left_split) {
                left_half()
                    card_tray(anchor=BOTTOM);
            } else {
                card_tray(anchor=BOTTOM);
            }
        }
    }
}

if (CheckRenderPieces(PIECES_LED_MOCK)) {
    render() {
        if (left_split) {
            left_half()
                led_mock(anchor=BOTTOM);
        } else {
            led_mock(anchor=BOTTOM);
        }
    }
}

module card_tray(anchor = CENTER, spin = 0, orient = UP) {
    card_tray_width = card_tray_size;
    card_tray_height = card_tray_size + card_tray_bracket_height * 2 + card_tray_bracket_offset * 2;
    card_tray_depth = card_tray_bracket_depth;

    attachable(anchor, spin, orient, size=[card_tray_width, card_tray_height, card_tray_depth]) {
        empty_attachable_context([card_tray_width, card_tray_height, card_tray_depth], anchor=CENTER) {
            position(BOTTOM) {
                inner_card_tray(anchor=BOTTOM);

                up(card_tray_base_thickness)
                    led_mock(anchor=BOTTOM);
            }

            color("pink")
                position(BOTTOM + FRONT)
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

            color("plum")
                position(BOTTOM + BACK)
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
                    difference() {
                        diff(remove="inner_cutout solder_cutout") {
                            // Outer tray profile
                            cuboid(
                                [
                                    card_tray_size,
                                    card_tray_size,
                                    card_tray_base_thickness + led_grid_thickness,
                                ],
                                rounding=card_tray_outer_rounding,
                                edges="Z",
                                anchor=BOTTOM
                            )

                                position(BOTTOM + RIGHT)
                                    tag("solder_cutout")
                                        left(led_grid_solder_pads_offset_right + card_tray_brim)
                                            cuboid(
                                                [
                                                    led_grid_solder_pads_width,
                                                    led_grid_solder_pads_height,
                                                    card_tray_base_thickness * 2,
                                                ],
                                                anchor=BOTTOM + RIGHT
                                            );

                            // Tray LED rim
                            cuboid(
                                [
                                    card_tray_led_rim,
                                    card_tray_led_rim,
                                    card_tray_thickness,
                                ],
                                anchor=BOTTOM
                            ) {
                                position(BOTTOM) {
                                    tag("inner_cutout") {
                                        // Void for the Optix panel
                                        up(card_tray_base_thickness + led_grid_base_thickness * 2) {
                                            cuboid(
                                                [
                                                    led_grid_pixels_size,
                                                    led_grid_pixels_size,
                                                    optix_thickness + led_grid_thickness + epsilon,
                                                ],
                                                anchor=BOTTOM
                                            );
                                        }

                                        // Void for the LED grid base - must be the full LED grid width
                                        up(card_tray_base_thickness)
                                            recolor("#aaaaaa")
                                                cuboid(
                                                    [
                                                        led_grid_size,
                                                        led_grid_size,
                                                        led_grid_base_thickness * 2,
                                                    ],
                                                    anchor=BOTTOM
                                                );
                                    }

                                    // Mock card acrylic size
                                    *recolor("#dddddd")
                                        up(card_tray_base_thickness + led_grid_thickness + optix_thickness)
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
        if (lo_rez_mocks) {
            down(mock_thickness / 2)
                recolor("#555555")
                    cuboid(
                        [
                            led_grid_size,
                            led_grid_size,
                            led_grid_base_thickness,
                        ],
                        anchor=BOTTOM
                    ) {
                        position(TOP) {
                            recolor("white")
                                cuboid(
                                    [
                                        led_grid_pixels_size,
                                        led_grid_pixels_size,
                                        led_grid_thickness - led_grid_base_thickness,
                                    ],
                                    anchor=BOTTOM
                                );
                        }
                    }
        } else {
            down(mock_thickness / 2)
                union() {
                    recolor("#555555")
                        cuboid(
                            [
                                led_grid_size,
                                led_grid_size,
                                led_grid_base_thickness,
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
                                                    led_grid_thickness - led_grid_base_thickness,
                                                ],
                                                anchor=BOTTOM
                                            );
                                    }
                                }
                            }
                        }

                    if (mock_optix) {
                        // Mock optix acrylic over the LEDS
                        up(led_grid_thickness)
                            recolor("#dddddd")
                                cuboid(
                                    [
                                        led_grid_pixels_size,
                                        led_grid_pixels_size,
                                        optix_thickness,
                                    ],
                                    anchor=BOTTOM
                                );
                    }
                }
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
