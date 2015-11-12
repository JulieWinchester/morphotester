=====================================================================
|                                                                   |
|                             MorphoTester                          |
|                               Ver. 1.0                            |
|                                                                   |
|                       Author: Julia Winchester                    |
|                   (julia.winchester@stonybrook.edu)               |
=====================================================================

MorphoTester is a scientific computing application for quantifying
topographic shape from three-dimensional triangulated meshes
representing anatomical shape data. Shape is described via three
metrics which characterize distinct aspects of form: curvature
(Dirichlet Normal Energy: Bunn et al., 2011; Winchester, in
preparation); relief (Relief Index: Ungar and M'Kirera, 2003; Boyer,
2008); and complexity (Orientation Patch Count Rotated: Evans et al.,
2007; Winchester, in preparation). Details on relevant methods can be
found in the listed publications. To run MorphoTester, execute
Morpho.py as a script via the Python interpreter. This application
provides a flexible engine for viewing 3D triangulated meshes and
calculating topographic metrics from individual files or directory
batches.

==================
File Type and Size
==================

MorphoTester accepts .ply Stanford PLY format surface mesh files.
Triangulated surface mesh files (that is, surfaces comprised of
multiple interconnected triangular polygons in three-dimensional
space) can be generally described by the number of triangular
polygons comprising each mesh. MorphoTester may be slow to load
surface meshes consisting of >500,000 faces or more depending on
computer speed, and DNE implicit fair mesh smoothing will be very
slow at >20,000 triangles. Previously published work using this
software has analyzed surface meshes simplified to 10,000 faces with
another application. Examples of applications capable of this include
Amira, Aviso, or the freeware application Meshlab. Future versions of
MorphoTester may include mesh simplification built in.

=======================
Processing Single Files
=======================

	1. Load single file by selecting the Open File button, navigating
	to desired file, and selecting Open. The surface can be inspected
	using the 3D viewer on the  right.

	2. Choose which topographic metrics are to be measured. Set
	parameters and optional procedures for DNE and OPCR calculation
	using the nearby Options button (See “DNE Options” and “OPCR
	Options” below for more detail).

	3. Select Process File, and wait. Values will be output shortly.

===============================
Batch Processing Multiple Files
===============================

	1. All .ply meshes to be measured should be located in a single
	directory.

	2. Select ‘Open Directory’ and navigate to desired directory for
	analysis. Select Open. No mesh will appear in the 3D viewer.

	3. As described above, choose which topographic metrics are to be
	measured, and use the Option menus to set parameters.

	4. Select Process Directory, and wait. Values will be output
	shortly. If an error occurs, this process will  halt entirely.

Batch processing produces a results file in the directory where
analyzed files are located. Results are provided as a tab-delineated
table of topographic values and file names, and may be opened in
Microsoft Excel or other applications.

===========
DNE Options
===========

If optional model smoothing for DNE is desired, check ‘DNE Implicit
Fairing Smooth.’ All previously published DNE calculations employ this
smoothing, with a smoothing iteration number of 3 and a step size of
0.1. This smoothing step can introduce possible application errors,
but it can also help reduce surface mesh noise which can
disproportionately affect DNE values. DNE can be calculated regardless
of whether implicit fairing is enabled. If implicit fairing is not
enabled, the iteration number and step size values are ignored.
	
Overall DNE can be disproportionately affected by intersections
between polygons with extreme angles such as often results from mesh
noise or erroneous sharp features on surface casts pre-scanning (see
‘Absurdly High DNE Values’ below). To address this, the ‘Outlier
Removal’ option culls individual polygonal DNE values above a user-
specified percentile amount. Outliers can be removed from the sample 
of energy quantities per polygon (energy density * polygon area) or
raw energy densities. Outlier removal at 99.9th percentile using
energy density * polygon area is currently recommended. Similarly, the
‘Condition number checking’ option removes individual polygon DNE 
values when the matrix comprising the face has a high condition 
number. High conditions numbers can indicate a matrix is singular 
(meaning further calculation of DNE cannot continue) and/or that the 
particular polygonal intersection is unreliable as a shape indicator 
due to extreme changes in DNE from minor changes in polygon position. 
‘Condition number checking’ should generally be left on, unless 
specific reasons indicate turning it off.

If Visualize DNE is checked, energy quantity values will be visualized
across a mesh surface as a heatmap. Relative DNE visualization uses
minimum and maximimum surface polygon energy quantities to bound the
heatmap legend, and is useful to plotting DNE across an individual
surface. Absolute DNE visualization allows the user to specify the
bounds of the heatmap plotting and is useful for comparing DNE between
two surfaces. 

============
OPCR Options
============

‘Minimum Patch Count’ defines the smallest size of a patch (in terms
of number of triangles comprising the patch) which will be counted
for OPC calculation (see Evans et al., 2007 for more detail). 3 is
the default value. If 'Visualize OPCR’ is checked, OPCR results for
single files will be depicted as colored patches on the mesh surface
in the 3D window viewer pane on the right. Patches are colored
according to their aspect, with each of the eight colors representing
an arc of 45 degrees. This visualization is similar to that provided
by Evans et al. (2007), but is different in that it represents
aspect-designated patches on a fully 3d mesh instead of a GIS grid of
single Z escalation values associated with XY coordinate pairs.

==========================
Changes from beta versions
==========================

Different RFI results between beta and current versions of 
MorphoTester:

Compared to latest release versions, some older betas of MorphoTester
generate different values for "outline area." Outline area is the 2D
area of a 3D surface as projected onto the XY plane (for dental
analyses this is often the occlusal plane). MorphoTester calculates 2D
projected area by producing a flat pixelated image of a surface,
counting surface pixels, and then multiplying this count by an area to
pixel ratio. The pixel counting method used here was updated midway
through beta development to ensure compatibility between Windows and
OSX environments. Any differences in outline area should be small,
usually around 1%.

Different DNE results with outlier removal between beta and current
versions of MorphoTester:

Unlike for RFI, the latest version of MorphoTester should be able to
replicate all DNE results obtained from any beta version. The base DNE
method is identical across all versions, but certain beta versions do
use different protocols for removing outliers, polygons with extremely
high energy values. Older beta versions removed polygons with energy
values above the 99th percentile across a surface mesh (for a mesh of
10,000 polygons, 100 outliers removed). Later beta versions changed
this to only remove polygons with energy values above the 99.9th
percentile (for a mesh of 10,000 polygons, 10 outliers removed). In
both of these cases, outliers were removed from values calculated as
energy density multiplied by polygon face area. One beta version,
0.2.0d, removed outliers from values calculated as raw energy
densities. The latest version of MorphoTester allows users to specify
outlier percentile and whether outliers should be removed from energy
densities * polygon areas or raw energy densities. Outlier removal at
99.9% using energy densities * polygon areas is currently recommended,
but trends of differences between specimens should be generally
similar regardless of approach.

============
Known Issues
============

CHOL errors

	This is the primary bug likely to be encountered with
	MorphoTester. It will only be encountered when measuring DNE with
	implicit fairing smoothing. This error relates to the matrices
	that comprise the surface data, and in practice it has mostly been
	encountered as a result of smoothing operations completed by Amira
	or Aviso. The simplest run-around to this problem, if implicit
	fairing is desired (for comparability to current DNE results for
	example), is to not use smoothing functions from Amira or Aviso.
	Meshlab works equally well for this purpose. For models already
	encountering this error, applying a 1 or 2-iteration Laplacian
	smooth using Meshlab will fix the problem while not effecting DNE
	values significantly.

Absurdly high DNE values

	DNE can be sensitive to certain kinds of surface noise or mesh
	artifacts that are not biological, such as long thin gaps in
	surface models, triangular polygons overlapping one another or
	sitting at bizarre angles, or accessory isolated polygon regions
	distinct from the surface to be analyzed. This is not an issue
	with MorphoTester, but instead requires care in preparing surface
	meshes to reduce noise or remove non-biological surface errors. In
	previously published DNE results, 100 iterations of smoothing has
	been used on simplified 10,000-face polygonal models for this
	purpose.

Fullscreen crashes (OS X only)

	Application is known to crash sometimes on exiting full-screen
	visualization of 3D meshes. 

DNE and OPCR visualization not working (Interpreted source code only)
	
	When using the newest versions of Mayavi and VTK6, visualization
	of DNE and OPCR may not function. This will be resolved soon.
