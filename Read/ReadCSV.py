def ReadCSV(content):
    """
    Read either a .csv file containing a RUC definition.

    Arguments:
        content str         content of the .csv file
    
    Outputs:
        mask    2D array    integer array defining the microstructure
        out     dict        dictionary of actual microstructure properties
    """

    # Import Modules
    import cv2
    import numpy as np
    
    # Get mask
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
    # Assume binary_mask is 0/1 array
    binary_mask = np.asarray(mask, dtype=np.uint8)  # convert to uint8
    binary_mask *= 255  # OpenCV expects 0 and 255

    # Calculate Radius
    # Assume binary_mask is 0/1 array
    binary_mask = (mask == 1).astype(np.uint8) * 255  # convert to uint8

    # Find connected components
    # connectivity=8 for diagonal connections
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask)

    h, w = binary_mask.shape
    fiber_indices = []

    for i in range(1, num_labels):  # skip 0 = background
        x, y, width, height, area = stats[i]

        # Skip if any part touches the image edge
        if x == 0 or y == 0 or x + width >= w or y + height >= h:
            continue
        fiber_indices.append(i)

    diameters = []
    for i in fiber_indices:
        area = stats[i, cv2.CC_STAT_AREA]
        diam = 2 * np.sqrt(area / np.pi)
        diameters.append(diam)

    diameters = np.array(diameters)
    if len(diameters) == 1:
        out['R'] = int(diameters.mean()) / 2
    else:
        out['R'] = diameters.mean() / 2

    # Calculate subcell dimensions
    out['NB'] = nx
    out['NG'] = ny

    return mask, out