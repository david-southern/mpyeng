include <BOSL2/std.scad>
use <lazy.scad>

printer_fudge = 0.15;

board_thickness = 5;
wire_26ga_outer_diameter = 1.6;

pixel_grid_size = 5;
pixel_size = 5;
pixel_cell_size = pixel_size + printer_fudge * 2;
pixel_cell_depth = 1.7;
bend_bars_inset = 0.4;

lock_bar_height = 3;

card_tray_width = 90;
card_tray_height = 120;
card_tray_thickness = 3;
card_rim_thickness = 9;
card_wall_width = 7;
card_waist_height = 70;

magnet_height = 3;
magnet_diameter = 8;
magnet_hole_diameter = magnet_diameter + printer_fudge * 2;
inset_piece_depth = 0.8;

lock_sphere_diameter = 2;
lock_bar_width = card_tray_width - card_wall_width * 2;

Flip = false;
Debug = false;

$fn = 43;

// Customizer limit module
module __Customizer_Limit__ () {}

strip_intra_pixel_spacing = 11.5;

pixel_cell_spacing = 12.5;
echo(str("Pixel Cell Spacing: ", pixel_cell_spacing));
intra_cell_spacing = pixel_cell_spacing - pixel_cell_size;
echo(str("Intra Cell Spacing: ", intra_cell_spacing));

bend_allowance_length = strip_intra_pixel_spacing / 2;
echo(str("Bend Allowance Length: ", bend_allowance_length));
bend_allowance_width = intra_cell_spacing / 2;
echo(str("Bend Allowance Width: ", bend_allowance_width));
bend_allowance_height = sqrt(bend_allowance_length ^ 2 - bend_allowance_width ^ 2);
echo(str("Bend Allowance Height: ", bend_allowance_height));

bend_bar_width = strip_intra_pixel_spacing - bend_allowance_length * 2;
echo(str("Bend Bar Width: ", bend_bar_width));

strip_seg_length = pixel_cell_size + bend_allowance_width * 2 + bend_bar_width;
strip_seg_thickness = 0.1;
strip_bend_length = bend_bar_width + bend_allowance_length * 2;



strip_width = 10;
strip_separator_width = pixel_cell_spacing - strip_width - bend_allowance_width * 2;
strip_pin_width = 1.7;
strip_pin_spacing = 3;



card_height = card_tray_height - card_wall_width;
card_width = card_tray_width - card_wall_width * 2;
card_waist_start = (card_height - card_waist_height - card_wall_width * 2) / 2;

card_tray_x_0 = 0; 
card_tray_x_1 = card_wall_width;
card_tray_x_2 = card_wall_width * 2;
card_tray_x_3 = card_tray_width - card_wall_width * 2;
card_tray_x_4 = card_tray_width - card_wall_width;
card_tray_x_5 = card_tray_width;

card_tray_y_0 = 0;
card_tray_y_1 = card_wall_width;
card_tray_y_2 = card_wall_width + card_waist_start;
card_tray_y_3 = card_wall_width + card_waist_start + card_wall_width;
card_tray_y_4 = card_wall_width + card_waist_start + card_wall_width + card_waist_height;
card_tray_y_5 = card_wall_width + card_waist_start + card_wall_width + card_waist_height + card_wall_width;
card_tray_y_6 = card_tray_height;

epsilon = 0.01; // Small value to ensure proper subtraction

render()
{
    if(Debug)
    {
        strips();
    }

    ry(Flip ? 180 : 0)
    {
        tx(card_tray_width)
        tz(lock_bar_height)
        rz(90)
        lock_bars();

        difference()
        {
            card_tray();

            lock_bars(punch=true);
        }

        lock_bar_assy();
    }
}

module flat_strip()
{
    strip_length = pixel_cell_spacing * pixel_grid_size;

    xcopies(strip_intra_pixel_spacing, pixel_grid_size)
    {
        color("darkgray")
        cube([strip_width, strip_length, 0.2], anchor=BOTTOM);

        color("orange")
        xcopies(strip_pin_spacing, 3)
        cube([strip_pin_width, strip_length, 0.2 + epsilon], anchor=BOTTOM);
    }
}

vcc_wire_depth = 1.5;
data_wire_depth = 1;
ground_wire_depth = 1.5;

module wiring_inset()
{
    strip_length = pixel_cell_spacing * pixel_grid_size;

    // +5V  wire run
    xcopies(strip_intra_pixel_spacing, 5)
    {
        if($idx > 0)
        {
            wire_run("red", 
                [
                    [-strip_pin_spacing, strip_length / 2, 0],
                    [0, 12, 0], 
                    [-strip_intra_pixel_spacing, 0, 0], 
                    [0, -12, 0],
                ],
                wire_26ga_outer_diameter * 2,
                wire_26ga_outer_diameter * vcc_wire_depth
            );
        }
    }

    // Data wire run
    xcopies(strip_intra_pixel_spacing, 5)
    {
        if($idx > 0)
        {
            data_delta = $idx % 2 == 0 ? 1 : -1;
            wire_run("yellow", 
                [
                    [0, data_delta * strip_length / 2, 0],
                    [0, data_delta * 7, 0], 
                    [-strip_intra_pixel_spacing, 0, 0], 
                    [0, -data_delta * 7, 0],
                ],
                wire_26ga_outer_diameter * 2,
                wire_26ga_outer_diameter * data_wire_depth
            );
        }
    }

    // Ground wire run
    xcopies(strip_intra_pixel_spacing, pixel_grid_size)
    {
        if($idx > 0)
        {
            wire_run("white", 
                [
                    [strip_pin_spacing, -strip_length / 2, 0],
                    [0, -12, 0], 
                    [-strip_intra_pixel_spacing, 0, 0], 
                    [0, 12, 0],
                ],
                wire_26ga_outer_diameter * 2,
                wire_26ga_outer_diameter * ground_wire_depth
            );
        }

    }
}

function sum_vectors(vec_list, start = 0, end = len(vec_list) - 1, zero_value = [0, 0, 0]) =
    end < start ? zero_value :
    vec_list[start] + sum_vectors(vec_list, start + 1, end);

module wire_run(
    wire_color, 
    wire_path, 
    wire_diameter_x, 
    wire_diameter_y
)
{
    if(len(wire_path) < 2)
    {
        echo("wire_run: Path must have at least two points");
    } else {
        tz(wire_diameter_y / 2)
        color(wire_color)
        {
            for(i = [0 : len(wire_path) - 2]) {
                start_vec = sum_vectors(wire_path, 0, i);
                end_vec = sum_vectors(wire_path, 0, i + 1);

                echo(str(wire_color, " Wire Segment ", i, ": ", start_vec, " to ", end_vec));
                extrude_from_to(start_vec, end_vec, convexity=4, twist=0, scale=1.0, slices=8)
                    square([wire_diameter_y, wire_diameter_x], center=true);

                if(i < len(wire_path) - 2)
                {
                    translate(end_vec)
                    cube([wire_diameter_x, wire_diameter_x, wire_diameter_y], center=true);
                }
            }
        }
    }
}

module card_tray()
{
    union()
    {
        difference()
        {
            tx(-card_tray_width/2)
            ty(-card_tray_height/2)
            {
                difference()
                {
                    card_outer_tray(card_tray_thickness);

                    // Inner tray
                    tz(-epsilon)
                    scale([1, 1, 10]) card_inner_tray();
                    tz(card_tray_thickness)
                    scale([1, 1, 10]) card_waist();
                }
                card_inner_tray();
            }

            // Magnet holes
            ty(card_wall_width / 2)
            xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
            ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
            cylinder(h=100, d=magnet_hole_diameter, center=true);

            pixel_grid();
        }

        // Board Support Posts
        ty(card_wall_width / 2)
        tz(card_tray_thickness - inset_piece_depth)
        xcopies(card_tray_width - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        ycopies(card_tray_height - card_wall_width * 4 - magnet_diameter / 2 * 0, 2)
        difference()
        {
            cylinder(h=board_thickness, d=magnet_hole_diameter, anchor = TOP);
            if($idx == 0) {
                cylinder(h=board_thickness * 3, d=wire_26ga_outer_diameter * 1.5, center=true);
            }
        }
    }
}

module card_waist()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_0, card_tray_y_3],
        [card_tray_x_5, card_tray_y_3],
        [card_tray_x_5, card_tray_y_4],
        [card_tray_x_0, card_tray_y_4]
    ]);
}

module card_inner_tray()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_1, card_tray_y_1],
        [card_tray_x_4, card_tray_y_1],
        [card_tray_x_4, card_tray_y_2],
        [card_tray_x_3, card_tray_y_3],
        [card_tray_x_3, card_tray_y_4],
        [card_tray_x_4, card_tray_y_5],
        [card_tray_x_4, card_tray_y_6],
        [card_tray_x_1, card_tray_y_6],
        [card_tray_x_1, card_tray_y_5],
        [card_tray_x_2, card_tray_y_4],
        [card_tray_x_2, card_tray_y_3],
        [card_tray_x_1, card_tray_y_2]
    ]);
}

module card_outer_tray(tray_depth = card_rim_thickness)
{
    linear_extrude(height=tray_depth)
    polygon([
        [card_tray_x_0, card_tray_y_0],
        [card_tray_x_2, card_tray_y_0],
        [card_tray_x_2, card_tray_y_1],
        [card_tray_x_3, card_tray_y_1],
        [card_tray_x_3, card_tray_y_0],
        [card_tray_x_5, card_tray_y_0],
        [card_tray_x_5, card_tray_y_2],
        [card_tray_x_4, card_tray_y_3],
        [card_tray_x_4, card_tray_y_4],
        [card_tray_x_5, card_tray_y_5],
        [card_tray_x_5, card_tray_y_6],
        [card_tray_x_0, card_tray_y_6],
        [card_tray_x_0, card_tray_y_5],
        [card_tray_x_1, card_tray_y_4],
        [card_tray_x_1, card_tray_y_3],
        [card_tray_x_0, card_tray_y_2]
    ]);
}

module pixel_grid() {
    color("pink")
    tz(-epsilon)
    xcopies(pixel_cell_spacing, pixel_grid_size)
    {
        ycopies(pixel_cell_spacing, pixel_grid_size)
        {
            cube([pixel_cell_size, pixel_cell_size, card_tray_thickness * 2], anchor=BOTTOM);
        }
    }
}

module lock_bar_assy()
{
    difference()
    {
        // Grid Base
        cube([
            lock_bar_width, 
            pixel_cell_spacing * pixel_grid_size + epsilon, 
            lock_bar_height + epsilon
        ], anchor=TOP);

        lock_bars(punch=true);

        color("blue")
        ycopies(pixel_cell_spacing, pixel_grid_size)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size + bend_allowance_width * 4,
            lock_bar_height + epsilon
        ], anchor = TOP);

        color("red")
        tz(-bend_allowance_height)
        xcopies(pixel_cell_spacing, pixel_grid_size)
        cube([
            strip_width + printer_fudge * 4,
            pixel_cell_spacing * pixel_grid_size + epsilon,
            lock_bar_height + epsilon
        ], anchor = TOP);

        color("magenta")
        ycopies(pixel_cell_spacing * pixel_grid_size, 2)
        cube([
            pixel_cell_spacing * pixel_grid_size + epsilon,
            pixel_cell_size + bend_allowance_width * 4,
            lock_bar_height + epsilon
        ], anchor = TOP);
    }
}

module lock_bars(punch=false)
{
    ycopies(pixel_cell_spacing, pixel_grid_size)
    lock_bar(punch=punch);
}

module lock_bar(punch=false)
{
    color(punch ? "magenta" : "green")
    {
        cube([
            lock_bar_width,
            pixel_cell_size,
            (lock_bar_height + epsilon)
        ], anchor = TOP);
        
        tz(-lock_bar_height / 2)
        ycopies(pixel_cell_size, 2)
        xcopies(lock_bar_width - pixel_cell_size, 2)
        sphere(d=lock_sphere_diameter);

        if(punch)
        {
            xcopies(lock_bar_width - lock_bar_height * 2, 2)
            tz(lock_bar_height / 2)
            cube([
                lock_bar_height * 2 + epsilon,
                pixel_cell_size,
                (lock_bar_height + epsilon)
            ], anchor = TOP);

            ycopies(pixel_cell_size, 2)
            xcopies(lock_bar_width - pixel_cell_size, 2)
            tz(-lock_sphere_diameter / 2)
            cyl(h = lock_bar_height * 2 + epsilon, d=lock_sphere_diameter * 0.8, anchor=TOP);

        }
    }

}

module strips(seg_width = strip_width)
{
    ty(pixel_cell_size / 2 + bend_allowance_width + bend_bar_width / 2)
    tz(pixel_cell_depth + strip_seg_thickness)
    cube([
        strip_width * (pixel_grid_size + 2),
        intra_cell_spacing,
        bend_allowance_height
    ], anchor=BOTTOM);

    xcopies(pixel_cell_spacing, pixel_grid_size)
    translate([
        -seg_width / 2,
        -pixel_cell_size / 2 - bend_allowance_width,
        pixel_cell_depth + strip_seg_thickness / 2
    ])
    ycopies(strip_seg_length, 7)
    strip_segment(seg_width);
}

module strip_segment(seg_width = strip_width)
{
    path = [
        [0, bend_allowance_height],
        [bend_allowance_width, 0], 
        [bend_allowance_width + pixel_cell_size, 0],
        [bend_allowance_width + pixel_cell_size + bend_allowance_width, bend_allowance_height], 
        [bend_allowance_width + pixel_cell_size + bend_allowance_width + bend_bar_width, bend_allowance_height], 
    ];

    color("red")
    rx(90)
    ry(90)
    linear_extrude(height=seg_width)
    stroke(path, width=strip_seg_thickness);
}

module wire_run_sweep(
    wire_color, 
    wire_path, 
    wire_diameter_x = wire_26ga_outer_diameter, 
    wire_diameter_y = wire_26ga_outer_diameter, 
    profile = false, 
    tangents = undef
)
{
    if(len(wire_path) < 2)
    {
        echo("wire_run: Path must have at least two points");
    } else {
        result_path = [ for (i=[0:len(wire_path) - 1]) sum_vectors(wire_path, 0, i) ];

        echo(str(wire_color, " Wire Sweep Path: ", result_path));
        color(wire_color)
        {
            path_sweep(
                square([wire_diameter_x, wire_diameter_y], center=true), 
                result_path,
                tangent = tangents,
                profiles = profile,
                width = 0.1
            );
        }
    }
}

module wiring_inset_bendy()
{
    strip_length = pixel_cell_spacing * pixel_grid_size;

    // +5V  wire run
    xcopies(strip_intra_pixel_spacing, 5)
    {
        if($idx > 0)
        {
            wire_run("red", 
                [
                    [strip_pin_spacing, strip_length / 2, 0],
                    [0, 1, 0], 
                    [0, printer_fudge, 0], 
                    [0, wire_26ga_outer_diameter / 2, -wire_26ga_outer_diameter / 2], 
                    [0, printer_fudge, 0],
                    [0, 12, 0], 
                    [0, printer_fudge, 0],
                    [-printer_fudge, 0, 0],
                    [-(strip_intra_pixel_spacing - printer_fudge * 2), 0, 0], 
                    [-printer_fudge, 0, 0],
                    [0, -printer_fudge, 0],
                    [0, -12, 0],
                    [0, -printer_fudge, 0],
                    [0, -wire_26ga_outer_diameter / 2, wire_26ga_outer_diameter / 2], 
                    [0, -printer_fudge, 0],
                    [0, -1, 0] 
                ],
                wire_26ga_outer_diameter * 2
            );
        }
    }

    // Data wire run
    xcopies(strip_intra_pixel_spacing, 5)
    {
        if($idx > 0)
        {
            wire_run("yellow", 
                [
                    [0, strip_length / 2, 0],
                    [0, 10, 0], 
                    [0, printer_fudge, 0],
                    [-printer_fudge, 0, 0],
                    [-(strip_intra_pixel_spacing - printer_fudge * 2), 0, 0], 
                    [-printer_fudge, 0, 0],
                    [0, -printer_fudge, 0],
                    [0, -10, 0],
                ]
            );
        }
    }

    // Ground wire run
    xcopies(strip_intra_pixel_spacing, pixel_grid_size)
    {
        if($idx > 0)
        {
            wire_run("white", 
                [
                    [-strip_pin_spacing, strip_length / 2, 0],
                    [0, 1, 0], 
                    [0, printer_fudge, 0], 
                    [0, wire_26ga_outer_diameter / 2, -wire_26ga_outer_diameter / 2], 
                    [0, printer_fudge, 0],
                    [0, 15, 0], 
                    [0, printer_fudge, 0],
                    [-printer_fudge, 0, 0],
                    [-(strip_intra_pixel_spacing - printer_fudge * 2), 0, 0], 
                    [-printer_fudge, 0, 0],
                    [0, -printer_fudge, 0],
                    [0, -15, 0],
                    [0, -printer_fudge, 0],
                    [0, -wire_26ga_outer_diameter / 2, wire_26ga_outer_diameter / 2], 
                    [0, -printer_fudge, 0],
                    [0, -1, 0] 
                ],
                wire_26ga_outer_diameter * 2
            );
        }

    }
}

