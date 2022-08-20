include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <BOSL/paths.scad>
use <BOSL/metric_screws.scad>
use <lazy.scad>

include <polyround.scad>
            
module round_rect_collar(interior_size, top_width, base_width, 
    collar_height, shoulder_height = undef, 
    inner_radius = undef, outer_radius = undef, shoulder_radius = undef, corner_radius = undef, base_radius = undef,
    corner_qual=11, profile_qual=7)
{
    ir = is_undef(inner_radius) ? top_width / 6 : inner_radius;
    or = is_undef(outer_radius) ? ir : outer_radius;
    sr = is_undef(shoulder_radius) ? ir : shoulder_radius;
    cr = is_undef(corner_radius) ? ir : corner_radius;
    br = is_undef(base_radius) ? 0 : base_radius;

    sh = is_undef(shoulder_height) ? 0 : shoulder_height;

    ix = interior_size.x / 2;
    iy = interior_size.y / 2;

    assert(is_num(ix));
    assert(ix >= 0);
    assert(is_num(iy));
    assert(iy >= 0);
    assert(is_num(top_width));
    assert(top_width >= 0);
    assert(is_num(base_width));
    assert(base_width >= 0);
    assert(is_num(collar_height));
    assert(collar_height >= 0);
    assert(is_num(sh));
    assert(sh >= 0);
    assert(is_num(ir));
    assert(ir >= 0);
    assert(is_num(or));
    assert(or >= 0);
    assert(is_num(sr));
    assert(sr >= 0);
    assert(is_num(cr));
    assert(cr >= 0);
    assert(is_num(br));
    assert(br >= 0);
    assert(is_num(sh));
    assert(sh >= 0);
    assert(is_num(corner_qual));
    assert(corner_qual >= 0);
    assert(is_num(profile_qual));
    assert(profile_qual >= 0);

    round_rect_collar_worker(ix, iy, top_width, base_width, 
        collar_height, sh, 
        ir, or, sr, cr, br,
        corner_qual, profile_qual);
}

module round_rect_collar_worker(ix, iy, top_width, base_width, 
    collar_height, sh, 
    ir, or, sr, cr, br,
    corner_qual, profile_qual)
{
    b4_shape_points=[
        [0, -sh, br],
        [0, collar_height, ir],
        [top_width, collar_height, or],
        [base_width, 0, sr],
        [base_width, -sh, br]
    ];
    
    shape_points=concat(
        [
            [0, 0, br],
            [0, sh + collar_height, ir],
            [top_width, sh + collar_height, or]
        ],
        sh > 0 ? [ [base_width, sh, sr] ] : [],
        [
            [base_width, 0, br]
        ]
    );

    shape = polyRound(shape_points, profile_qual);
    
    // Previously I was starting and ending the rim at x = 0, however when I did that, the resulting object was not
    // valid (a difference() on it would throw an error).  I had to fix up the non-manifold result in another 3D editor
    // before I could use if for further CSG. By leaving a bit of a gap here and then filling the gap with a second 
    // extrusion, I get a valid result.

    gap_constant = min(ix / 10, 0.1);

    rim_points=[
        [-gap_constant, -iy, 0],
        [-ix, -iy,  cr],
        [-ix,  iy,  cr],
        [ ix,  iy,  cr],
        [ ix, -iy,  cr],
        [gap_constant, -iy, 0],
    ];
    
    rail = [ for (i = polyRound(rim_points, corner_qual)) [ i.x, i.y, 0] ];

    gap_points=[
        [gap_constant * 2, -iy, 0],
        [-gap_constant * 2, -iy, 0],
    ];

    extrude_2dpath_along_3dpath(shape, rail, ang=-90);
    extrude_2dpath_along_3dpath(shape, gap_points, ang=-90);
}

module circle_collar(interior_diameter, top_width, base_width, 
    collar_height, shoulder_height = undef, 
    inner_radius = undef, outer_radius = undef, shoulder_radius = undef, base_radius = undef,
    circle_qual=11, profile_qual=7, axis_scale = [1, 1])
{
    assert(is_num(interior_diameter));
    assert(interior_diameter >= 0);
    
    assert(is_num(top_width));
    assert(top_width >= 0);
    assert(is_num(base_width));
    assert(base_width >= 0);
    assert(is_num(collar_height));
    assert(collar_height >= 0);
    assert(is_num(circle_qual));
    assert(circle_qual > 1);
    assert(is_num(profile_qual));
    assert(profile_qual > 1);
    assert(is_list(axis_scale));

    ir = is_undef(inner_radius) ? top_width / 6 : inner_radius;
    or = is_undef(outer_radius) ? ir : outer_radius;
    sr = is_undef(shoulder_radius) ? ir : shoulder_radius;
    br = is_undef(base_radius) ? 0 : base_radius;

    shoulder_height = is_undef(shoulder_height) ? 0 : shoulder_height;

    assert(is_num(shoulder_height));
    assert(shoulder_height >= 0);
    assert(is_num(inner_radius));
    assert(inner_radius >= 0);
    assert(is_num(outer_radius));
    assert(outer_radius >= 0);
    assert(is_num(shoulder_radius));
    assert(shoulder_radius >= 0);
    
    circle_collar_worker(interior_diameter, top_width, base_width, 
        collar_height, shoulder_height, 
        ir, or, sr, br,
        circle_qual, profile_qual, axis_scale);
}

module circle_collar_worker(interior_diameter, top_width, base_width, 
    collar_height, shoulder_height, 
    ir, or, sr, br,
    circle_qual=11, profile_qual=7, axis_scale = [1, 1])
{
    shape_points=concat(
        [
            [0, 0, br],
            [shoulder_height + collar_height, 0, ir],
            [shoulder_height + collar_height, top_width, or]
        ],
        shoulder_height > 0 ? [ [shoulder_height, base_width, sr] ] : [],
        [ [0, base_width, br] ]
    );

    shape = polyRound(shape_points, profile_qual);

    // txy(-interior_diameter / 2, -base_width * 2.1 - collar_height - shoulder_height) rx(90) rz(90) polygon(shape);

    rail_angle = 90 / circle_qual;
    
    // Overlap the segments to solve the manifold issue described in round_rect_collar above.
    start_angle = -rail_angle / 2;
    end_angle = 90 + rail_angle / 2;
    
    rail = [
        for (a=[start_angle:rail_angle:end_angle]) [
            interior_diameter / 2 * cos(a), 
            interior_diameter / 2 *sin(a), 
            0
        ]
    ];

    zrot_copies(n=4)
    extrude_2dpath_along_3dpath(shape, rail, ang = -90);
}
