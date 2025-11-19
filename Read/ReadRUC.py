def ReadRUC(content):
    """
    Read either a .txt or .mac file containing a RUC definition.

    Arguments:
        content str         content of the .mac/.txt file
    
    Outputs:
        mask    2D array    integer array defining the microstructure
        out     dict        dictionary of actual microstructure properties
    """
    
    # Import Modules
    import cv2
    import numpy as np

    # Separate into lines
    lines = content.strip().splitlines()

    # Find *RUC section
    flag = 0
    end_line = len(lines)
    for i, line in enumerate(lines):
        if "*RUC" in line:
            start_line = i
            flag = 1
            continue
        if flag == 1:
            if "*" in line:
                end_line = i
                break

    # Get subcells dimensions
    H = ''
    flag_h = 0
    for i in range(start_line, end_line):
        if "H=" in lines[i]:
            H = H + lines[i].split('H=')[1]
            flag_h = 1
            continue
        if flag_h == 1:
            if "=" in lines[i]:
                break
            else:
                H = H + lines[i]
    H = H.replace('&','')
    H = H.replace('\n','')
    H = H.replace(' ','')
    H = [float(x) for x in H.split(",") if x.strip() != ""]
    NB = len(H)

    L = ''
    flag_l = 0
    for i in range(start_line, end_line):
        if "L=" in lines[i]:
            L = L + lines[i].split('L=')[1]
            flag_l = 1
            continue
        if flag_l == 1:
            if "=" in lines[i]:
                break
            else:
                L = L + lines[i]
    L = L.replace('&','')
    L = L.replace('\n','')
    L = L.replace(' ','')
    L = [float(x) for x in L.split(",") if x.strip() != ""]
    NG = len(L)

    # Get the subcell values
    mask = np.zeros(shape=(NB,NG))

    for j in range(NB):
        SM = ''
        flag_m = 0
        for i in range(start_line, end_line):
            if flag_m == 0:
                if "SM=" in lines[i]:
                    SM = SM + lines[i].split('SM=')[1]
                    flag_m = 1
                    continue
            if flag_m == 1:
                if "SM=" in lines[i]:
                    start_line = i
                    break
                else:
                    SM = SM + lines[i]
        SM = SM.replace('&','')
        SM = SM.replace('\n','')
        SM = SM.replace(' ','')
        SM = [int(x) for x in SM.split(",") if x.strip() != ""]
        mask[j,:] = SM
    mask = mask.astype(int)

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
    out['R'] = diameters.mean() / 2

    # Calculate subcell dimensions
    out['NB'] = nx
    out['NG'] = ny

    return mask, out