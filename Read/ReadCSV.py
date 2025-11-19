def ReadCSV(content):
    # Import Modules
    import numpy as np
    mask = np.array([list(map(int, line.split(','))) for line in content.strip().splitlines()])

    # Calculate actual values
    out = {
            'VF':None,
           'R':None,
           'NB':None,
           'NG':None,
           'F':1,
           'M':2
           }
    
    # Set Dimensions
    nx = len(mask[0,:])
    ny = len(mask[:,0])

    # Calculate Volume Fraction
    out['VF'] = np.sum(mask == 1) / (nx * ny)

    # Calculate Radius
    out['R'] = np.sum(mask[:,int(nx/2)] == 1)/2

    # Calculate subcell dimensions
    out['NB'] = nx
    out['NG'] = ny

    return mask, out