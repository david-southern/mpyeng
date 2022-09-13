include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <BOSL/paths.scad>
use <BOSL/metric_screws.scad>

include <polyround.scad>

$fn = 7;



shape = [[-4,0],[5,3],[0,7]];

curvy_path = concat(
    [for (a=[30:30:180]) [50*cos(a)+50, 50*sin(a), 20*sin(a)]],
    [for (a=[330:-30:180]) [50*cos(a)-50, 50*sin(a), 20*sin(a)]]
);
rail = [ [0, 0, 0], [0, 0, 3] ];
    
extrude_2dpath_along_3dpath(shape, rail, ang=90);
    
    
    
/* 
manyPoints=[[-4,0],[5,3],[0,7],[8,7],[20,20],[10,0]];
polyPoints=[[-4,0],[5,3],[0,7]];

color("magenta")
difference()
{
    rail = [ [0, 0, 0], [0, 0, 3] ];
    // extrude_2dpath_along_3dpath(polyPoints, rail, ang=-90);

    translate([0, 0, 1])
    cuboid([20, 20, 1]);
}

*/