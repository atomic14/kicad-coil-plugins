'''
Biot-Savart Magnetic Field Calculator v4.3
Mingde Yin
Ryan Zazo

All lengths are in cm, B-field is in G

from - https://github.com/vuthalab/biot-savart
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.ticker as ticker

'''
Feature Wishlist:
    improve plot_coil with different colors for different values of current

    accelerate integrator to use meshgrids directly instead of a layer of for loop

    get parse_coil to use vectorized function instead of for loop
'''

def parse_coil(filename):
    '''
    Parses 4 column CSV into x,y,z,I slices for coil.

    Each (x,y,z,I) entry defines a vertex on the coil.

    The current I of the vertex, defines the amount of current running through the next segment of coil, in amperes.

    i.e. (0, 0, 1, 2), (0, 1, 1, 3), (1, 1, 1, 4) means that:
    - There are 2 amps of current running between points 1 and 2
    - There are 3 amps of current running between points 2 and 3
    - The last bit of current is functionally useless.
    '''
    with open(filename, "r") as f: return np.array([[eval(i) for i in line.split(",")] for line in f.read().splitlines()]).T

def slice_coil(coil, steplength):
    '''
    Slices a coil into pieces of size steplength.

    If the coil is already sliced into pieces smaller than that, this does nothing.
    '''
    def interpolate_points(p1, p2, parts):
        '''
        Produces a series of linearly spaced points between two given points in R3+I

        Linearly interpolates X,Y,Z; but keeps I the SAME

        i.e. (0, 2, 1, 3), (3, 4, 2, 5), parts = 2:
        (0, 2, 1, 3), (1.5, 3, 1.5, 3), (3, 4, 2, 5)
        '''
        return np.column_stack((np.linspace(p1[0], p2[0], parts+1), np.linspace(p1[1], p2[1], parts+1),
                np.linspace(p1[2], p2[2], parts+1), p1[3] * np.ones((parts+1))))

    newcoil = np.zeros((1, 4)) # fill column with dummy data, we will remove this later.

    segment_starts = coil[:,:-1]
    segment_ends = coil[:,1:]
    # determine start and end of each segment

    segments = segment_ends-segment_starts
    segment_lengths = np.apply_along_axis(np.linalg.norm, 0, segments)
    # create segments; determine start and end of each segment, as well as segment lengths

    # chop up into smaller bits (elements)

    stepnumbers = (segment_lengths/steplength).astype(int)
    # determine how many steps we must chop each segment into

    for i in range(segments.shape[1]):
        newrows = interpolate_points(segment_starts[:,i], segment_ends[:,i], stepnumbers[i])
        # set of new interpolated points to feed in
        newcoil = np.vstack((newcoil, newrows))

    if newcoil.shape[0] %2 != 0: newcoil = np.vstack((newcoil, newcoil[-1,:]))
    ## Force the coil to have an even number of segments, for Richardson Extrapolation to work

    return newcoil[1:,:].T # return non-dummy columns

def calculate_field(coil, x, y, z):
    '''
    Calculates magnetic field vector as a result of some position and current x, y, z, I
    [In the same coordinate system as the coil]

    Coil: Input Coil Positions, already sub-divided into small pieces using slice_coil
    x, y, z: position in cm
    
    Output B-field is a 3-D vector in units of G
    '''
    FACTOR = 0.1 # = mu_0 / 4pi when lengths are in cm, and B-field is in G

    def bs_integrate(start, end):
        '''
        Produces tiny segment of magnetic field vector (dB) using the midpoint approximation over some interval

        TODO for future optimization: Get this to work with meshgrids directly
        '''
        dl = (end-start).T
        mid = (start+end)/2
        position = np.array((x-mid[0], y-mid[1], z-mid[2])).T
        # relative position vector
        mag = np.sqrt((x-mid[0])**2 + (y-mid[1])**2 + (z-mid[2])**2)
        # magnitude of the relative position vector

        return start[3] * np.cross(dl[:3], position) / np.array((mag ** 3, mag ** 3, mag ** 3)).T
        # Apply the Biot-Savart Law to get the differential magnetic field
        # current flowing in this segment is represented by start[3]

    B = 0

    # midpoint integration with 1 layer of Richardson Extrapolation
    starts, mids, ends = coil[:,:-1:2], coil[:,1::2], coil[:,2::2]

    for start, mid, end in np.nditer([starts, mids, ends], flags=['external_loop'], order='F'):
        # use numpy fast indexing
        fullpart = bs_integrate(start, end) # stage 1 richardson
        halfpart = bs_integrate(start, mid) + bs_integrate(mid, end) # stage 2 richardson

        B += 4/3 * halfpart - 1/3 * fullpart # richardson extrapolated midpoint rule
    
    return B * FACTOR # return SUM of all components as 3 (x,y,z) meshgrids for (Bx, By, Bz) component when evaluated using produce_target_volume

def produce_target_volume(coil, box_size, start_point, vol_resolution):
    '''
    Generates a set of field vector values for each tuple (x, y, z) in the box.
​
    Coil: Input Coil Positions in format specified above, already sub-divided into small pieces
    box_size: (x, y, z) dimensions of the box in cm
    start_point: (x, y, z) = (0, 0, 0) = bottom left corner position of the box
    vol_resolution: Spatial resolution (in cm)
    '''
    x = np.linspace(start_point[0], box_size[0] + start_point[0],int(box_size[0]/vol_resolution)+1)
    y = np.linspace(start_point[1], box_size[1] + start_point[1],int(box_size[1]/vol_resolution)+1)
    z = np.linspace(start_point[2], box_size[2] + start_point[2],int(box_size[2]/vol_resolution)+1)
    # Generate points at regular spacing, incl. end points
    
    Z, Y, X = np.meshgrid(z, y, x, indexing='ij')
    # NOTE: Requires axes to be flipped in order for meshgrid to have the correct dimensional order

    return calculate_field(coil, X,Y,Z)

def get_field_vector(targetVolume, position, start_point, volume_resolution):
    '''
    Returns the B vector [Bx, By, Bz] components in a generated Target Volume at a given position tuple (x, y, z) in a coordinate system

    start_point: (x, y, z) = (0, 0, 0) = bottom left corner position of the box
    volume_resolution: Division of volumetric meshgrid (generate a point every volume_resolution cm)
    '''
    relativePosition = ((np.array(position) - np.array(start_point)) / volume_resolution).astype(int)
    # adjust to the meshgrid's system

    if (relativePosition < 0).any(): return ("ERROR: Out of bounds! (negative indices)")

    try: return targetVolume[relativePosition[0], relativePosition[1], relativePosition[2], :]
    except: return ("ERROR: Out of bounds!")
    # basic error checking to see if you actually got a correct input/output

'''
- If you are indexing a targetvolume meshgrid on your own, remember to account for the offset (starting point), and spatial resolution
- You will need an index like <relativePosition = ((np.array(position) - np.array(start_point)) / volume_resolution).astype(int)>
'''

def write_target_volume(input_filename,output_filename, box_size, start_point, 
                        coil_resolution=1, volume_resolution=1):
    '''
    Takes a coil specified in input_filename, generates a target volume, and saves the generated target volume to output_filename.

    box_size: (x, y, z) dimensions of the box in cm
    start_point: (x, y, z) = (0, 0, 0) = bottom left corner position of the box AKA the offset
    coil_resolution: How long each coil subsegment should be
    volume_resolution: Division of volumetric meshgrid (generate a point every volume_resolution cm)
    '''
    coil = parse_coil(input_filename) 
    chopped = slice_coil(coil, coil_resolution)
    targetVolume = produce_target_volume(chopped, box_size, start_point, volume_resolution)

    with open(output_filename, "wb") as f: np.save(f, targetVolume)
    # stored in standard numpy pickle form

def read_target_volume(filename):
    '''
    Takes the name of a saved target volume and loads the B vector meshgrid.
    Returns None if not found.
    '''
    targetVolume = None

    try:
        with open(filename, "rb") as f:
            targetVolume = np.load(f)
        return targetVolume
    except:
        pass

## plotting routines

def plot_fields(Bfields,box_size,start_point,vol_resolution,which_plane='z',level=0,num_contours=50):
    '''
    Plots the set of Bfields in the given region, at the specified resolutions. 
    
    Bfields: A 4D array of the Bfield.
    box_size: (x, y, z) dimensions of the box in cm
    start_point: (x, y, z) = (0, 0, 0) = bottom left corner position of the box AKA the offset
    vol_resolution: Division of volumetric meshgrid (generate a point every volume_resolution cm)
    which_plane: Plane to plot on, can be "x", "y" or "z"
    level : The "height" of the plane. For instance the Z = 5 plane would have a level of 5
    num_contours: THe amount of contours on the contour plot.
    
    '''

    # filled contour plot of Bx, By, and Bz on a chosen slice plane
    X = np.linspace(start_point[0], box_size[0] + start_point[0],int(box_size[0]/vol_resolution)+1)
    Y = np.linspace(start_point[1], box_size[1] + start_point[1],int(box_size[1]/vol_resolution)+1)
    Z = np.linspace(start_point[2], box_size[2] + start_point[2],int(box_size[2]/vol_resolution)+1)

    print(Z)

    if which_plane=='x':

        converted_level = np.where(X >= level)
        B_sliced = [Bfields[converted_level[0][0],:,:,i].T for i in range(3)]
        x_label,y_label = "y","z"
        x_array,y_array = Y,Z
    elif which_plane=='y':
        converted_level = np.where(Y >= level)
        B_sliced = [Bfields[:,converted_level[0][0],:,i].T for i in range(3)]
        x_label,y_label = "x","z"
        x_array,y_array = X,Z
    else:
        converted_level = np.where(Z >= level)
        print(converted_level[0][0])
        B_sliced = [Bfields[:,:,converted_level[0][0],i].T for i in range(3)]
        x_label,y_label = "x","y"
        x_array,y_array = X,Y
    
    Bmin,Bmax = np.amin(B_sliced),np.amax(B_sliced)
    
    component_labels = ['x','y','z']
    fig,axes = plt.subplots(nrows=4,ncols=1,figsize=(10,40))
    axes[0].set_ylabel(y_label + " (cm)")

    for i in range(3):
        contours = axes[i].contourf(x_array,y_array,B_sliced[i],
                                    vmin=Bmin,vmax=Bmax,
                                    cmap=cm.magma,levels=num_contours)
        axes[i].set_xlabel(x_label + " (cm)")
        axes[i].set_title("$\mathcal{B}$"+"$_{}$".format(component_labels[i]))
    
    axes[3].set_aspect(100)
    fig.colorbar(contours,cax=axes[3],extend='both')
    
    plt.tight_layout()

    plt.show()
    
def plot_coil(*input_filenames):
    '''
    Plots one or more coils in space.
    
    input_filenames: Name of the files containing the coils. 
    Should be formatted appropriately.
    '''
    fig = plt.figure()
    tick_spacing = 2
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("$x$ (cm)")
    ax.set_ylabel("$y$ (cm)")
    ax.set_zlabel("$z$ (cm)")

    for input_filename in input_filenames:
        coil_points = np.array(parse_coil(input_filename))
        
        ax.plot3D(coil_points[0,:],coil_points[1,:],coil_points[2,:],lw=2)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:
        axis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    plt.tight_layout()
    plt.show()
    
    
def create_B_x_rectangle(name,p0=[-21.59,-38.1,-21.59,1],L = 76.20,W= 43.18):
    '''
    Creates a rectangle of the Y-Z plane that produces a B_x field.
    
    name: filename to output to. Should be a .txt file.
    p0: [x0,y0,z0,Current] Starting point of the rectangle.
    L: Length (on Z)
    W: Width (on y)
    '''
    f = open(name,"w")

    p1 = [p0[0],p0[1]+W,p0[2],p0[3]]
    p2 = [p0[0],p0[1]+W,p0[2]+L ,p0[3]]
    p3 = [p0[0],p0[1],p0[2]+L,p0[3]]


    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p1)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p2)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p3)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)
    f.close()


def create_B_y_rectangle(name,p0=[-21.59,-38.1,-21.59,1], L = 76.20, D= 43.18):

    '''
    Creates a rectangle of the X-Z plane that produces a B_y field.
    
    name: filename to output to. Should be a .txt file.
    p0: [x0,y0,z0,Current] Starting point of the rectangle.
    L: Length (on Z)
    D: Depth (on X)
    '''
    f = open(name,"w")

    p1 = [p0[0], p0[1] , p0[2]+L, p0[3]]
    p2 = [p0[0] + D , p0[1] , p0[2]+L, p0[3]]
    p3 = [p0[0] + D , p0[1], p0[2], p0[3]]

    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p1)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p2)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p3)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)
    f.close()

def create_B_z_rectangle(name,p0=[-26.67,-26.67,-26.67,1], H= 53.340, DD = 53.340):
    '''
    Creates a rectangle of the X-Y plane that produces a B_z field.
    
    name: filename to output to. Should be a .txt file.
    p0: [x0,y0,z0,Current] Starting point of the rectangle.
    H: Height (on Y)
    DD: Depth (on X)
    '''
    f = open(name,"w")

    p1 = [p0[0] + DD, p0[1], p0[2], p0[3]]
    p2 = [p0[0] + DD, p0[1]+H, p0[2], p0[3]]
    p3 = [p0[0], p0[1]+H, p0[2], p0[3]]

    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p1)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p2)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p3)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    line = str(p0)
    line = line[1:len(line)-1] + "\n"
    f.write(line)

    f.close()
    
def helmholtz_coils(fname1, fname2, numSegments, radius, spacing, current):
    '''
    Creates a pair of Helmholtz Coils that are parallel to the X-Y plane.
    
    fname1: Name of the file where the first coil will be saved.
    fname2: Name of the file where the second coil will be saved.
    numSegments: Number of segments per coil
    radius: Radius of the coils
    spacing: Spacing between the coils. The first coil will be located at -spacing/2 and the 2nd coil will be located at spacing/2 on the Z plane
    current: The current that goest through each coil.
    '''
    f = open(fname1,"w")
    line = ""
    for i in range(0,numSegments,1):
        line = str(np.cos(2*np.pi*(i)/(numSegments-1))*radius) + "," + str(np.sin(2*np.pi*(i)/(numSegments-1))*radius) + "," + str(-spacing/2.0) + "," + str(current) + "\n"
        f.write(line)
    f.close()

    f = open(fname2,"w")
    line = ""
    for i in range(0,numSegments,1):
        line = str(np.cos(2*np.pi*(i)/(numSegments-1))*radius) + "," + str(np.sin(2*np.pi*(i)/(numSegments-1))*radius) + "," + str(spacing/2.0) + "," + str(current) + "\n"
        f.write(line)
    f.close()
    
    
def create_Bx_circle(fname, numSegments, radius, spacing, current, center):
    '''
    Creates a coil on the Y-Z plane that produces a B_x field.
    
    fname: Name of the file where the first coil will be saved.
    numSegments: Number of segments per coil
    radius: Radius of the coil
    spacing: Spacing between the coil and the Y-Z plane
    current: The current that goest through the coil.
    center: (y,z) The center of the coil on the Y-Z plane
    '''
    f = open(fname,"w")
    line = ""
    for i in range(0,numSegments,1):
        line = str(spacing) + "," + str(np.cos(2*np.pi*(i)/(numSegments-1))*radius + center[0])  + "," + str(np.sin(2*np.pi*(i)/(numSegments-1))*radius + center[1]) +  "," + str(current) + "\n"
        f.write(line)
    f.close()
    
    
def create_By_circle(fname, numSegments, radius, spacing, current, center):
    '''
    Creates a coil on the X-Z plane that produces a B_y field.
    
    fname: Name of the file where the first coil will be saved.
    numSegments: Number of segments per coil
    radius: Radius of the coil
    spacing: Spacing between the coil and the X-Z plane
    current: The current that goest through the coil.
    center: (x,z) The center of the coil on the X-Z plane
    '''
    f = open(fname,"w")
    line = ""
    for i in range(0,numSegments,1):
        line = str(np.cos(2*np.pi*(i)/(numSegments-1))*radius + center[0])  + "," + str(spacing) + "," + str(np.sin(2*np.pi*(i)/(numSegments-1))*radius + center[1]) +  "," + str(current) + "\n"
        f.write(line)
    f.close()
    
    
def create_Bz_circle(fname, numSegments, radius, spacing, current, center):
    '''
    Creates a coil on the X-Y plane that produces a B_z field.
    
    fname: Name of the file where the first coil will be saved.
    numSegments: Number of segments per coil
    radius: Radius of the coil
    spacing: Spacing between the coil and the X-Y plane
    current: The current that goest through the coil.
    center: (x,y) The center of the coil on the X-Y plane
    '''
    f = open(fname,"w")
    line = ""
    for i in range(0,numSegments,1):
        line = str(np.cos(2*np.pi*(i)/(numSegments-1))*radius + center[0]) + "," + str(np.sin(2*np.pi*(i)/(numSegments-1))*radius + center[1]) + "," + str(spacing) + "," + str(current) + "\n"
        f.write(line)
    f.close()

