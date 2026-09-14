import matplotlib.pyplot as plt  # plotting
import numpy as np
from matplotlib.widgets import PolygonSelector
from skimage.draw import polygon



def select_main_area(img):
    plt.clf()


    #fig, ax = plt.subplots()
    fig = plt.gcf()
    ax = plt.gca()

    ax.imshow(img,cmap="inferno")
    
    #fig.show()
    selector = PolygonSelector(ax, lambda *args: None,props=dict(color='w', linestyle='-', linewidth=2, alpha=0.5))
    plt.show()
    


    plt.clf()
    
    vertices = np.array(selector.verts)
    if (len(vertices)):
        img = np.zeros(img.shape,dtype=bool)
        rr, cc = polygon(vertices[:,1], vertices[:,0], img.shape)
        img[rr,cc] = 1
    else:
        img = np.ones(img.shape,dtype=bool)


    return img





def filter_roi(img, roi):
    plt.clf()

    """
    print(" -> Please right click on the ROIs to remove. Mid click to cancel, enter to confirm.")
    plt.imshow(img,cmap="gist_gray")
    plt.imshow(roi,alpha=.3,cmap="okabe_ito")
    pts = plt.ginput(n=-1,mouse_add = 3,mouse_pop = 2, mouse_stop = None,timeout = -1)
    plt.show()
    """


    #fig, ax = plt.subplots()
    fig = plt.gcf()
    ax = plt.gca()
    ax.imshow(img,cmap="gist_gray")
    ax.imshow(roi, alpha=.3, cmap="Set2")

    points = []
    finished = [False]

    def on_click(event):
        if event.inaxes != ax or event.xdata is None:
            return
        if event.button == 3:          # right click → add (matches your mouse_add=3)
            points.append((event.xdata, event.ydata))
            ax.plot(event.xdata, event.ydata, 'r+')   # optional visual feedback
            fig.canvas.draw_idle()
        elif event.button == 2:        # middle click → pop (matches your mouse_pop=2)
            if points:
                points.pop()
                # re-plot markers if you drew them...
                fig.canvas.draw_idle()

    def on_key(event):
        if event.key == 'enter':
            plt.close(fig)

    # These three connections guarantee clean exit:
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('close_event', lambda e: finished.__setitem__(0, True))

    plt.show()  # blocks until window closes or Enter is pressed — no hang

    pts=points
    #print(pts.shape,pts)

    #print(np.array(pts,dtype=int))

    for i in range(len(pts)):
        loc_y = int(pts[i][1])
        loc_x = int(pts[i][0])

        loc_roi = roi[loc_y,loc_x]
        if (loc_roi != 0):
            roi[roi==loc_roi]=0
            #print("Removing ",loc_roi)
            if (loc_roi %2 ==0): # even number, remove also the previous
                roi[roi==loc_roi-1] = 0
                #print("Removing", loc_roi+1)
            else: # odd, remove also the next
                roi[roi==loc_roi+1] = 0
                #print("Removing", loc_roi-1)

    
    #plt.imshow(img,cmap="gist_gray")
    #plt.imshow(roi,alpha=.3,cmap="okabe_ito")
    #pts = plt.ginput(n=-1,mouse_add = 3,mouse_pop = 2, mouse_stop = None,timeout = -1)
    #plt.title("Right click to remove rois, PRESS ENTER before closing")
    plt.show()


    ##### Re-order
    for i in range(2,np.amax(roi)+1):
        curr_idx = i
        while (np.sum(roi==curr_idx-1)==0 and curr_idx>1 and np.sum(roi==curr_idx)>0):
            #print("Moving ", curr_idx," to ", curr_idx-1)
            roi[roi==curr_idx] = curr_idx-1
            curr_idx = curr_idx-1
        

    return roi
