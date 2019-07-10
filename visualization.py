import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

"""
    Save a bitmap image to file.
"""
def save_image(bitmap, name, path=".\\img\\"):
    plt.axis("off")
    save_path = os.path.join(path, name) + ".png"
    plt.imshow(bitmap, interpolation="nearest", cmap=plt.cm.gray, origin="upper")
    plt.savefig(save_path)
    #plt.imsave(save_path, bitmap, cmap=plt.cm.gray)

"""
    Display a bitmap image.
"""
def show_image(bitmap):
    plt.axis("off")
    plt.imshow(bitmap, interpolation="nearest", cmap=plt.cm.gray, origin="upper")
    plt.show()

"""
    Combine a set of bitmaps into a single image
"""
def render_image_set(bitmaps, title):
    plt.clf()
    bitmap = np.concatenate(bitmaps, axis=1)
    bitmap = np.dstack([bitmap, bitmap, bitmap])
    plt.title(title)
    return bitmap

"""
    Display a pair of glyphs side-by-side along with their hausdorff distances, 
    highlighting the key contributing points.
"""
def render_distance_adjacent(char1, char2, bitmap1, bitmap2, points1, points2, dist1, dist2):
    plt.clf()
    bitmap = np.concatenate((bitmap1, bitmap2), axis=1)
    
    if points1 is not None or points2 is not None:
        bitmap = np.dstack([bitmap, bitmap, bitmap])
            
        mid_y = int(bitmap.shape[0]/2)
        mid_x = int(bitmap.shape[1]/2)

        p1 = mpatches.Patch(color="red", label="sup$_{0}$ inf$_{1}$ d({0},{1}): {2:.2f}".format(char1, char2, dist1))
        p2 = mpatches.Patch(color="aqua", label="sup$_{1}$ inf$_{0}$ d({0},{1}): {2:.2f}".format(char1, char2, dist2))
        plt.legend(handles=[p1, p2], bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

    if points1 is not None:
        bitmap[points1[0][0], points1[0][1]] = [1, 0, 0]
        bitmap[points1[1][0], points1[1][1]] = [0, 1, 1]

        highlight_point(points1[0][1], points1[0][0], mid_x, mid_y, "red")
        highlight_point(points1[1][1], points1[1][0], mid_x, mid_y, "cyan")

    if points2 is not None:
        # Adjust column of second bitmap by width of first
        new_points2 = [(p[0], p[1] + bitmap1.shape[1]) for p in points2]
        bitmap[new_points2[0][0], new_points2[0][1]] = [1, 0, 0]
        bitmap[new_points2[1][0], new_points2[1][1]] = [0, 1, 1]

        highlight_point(new_points2[0][1], new_points2[0][0], mid_x, mid_y, "red")
        highlight_point(new_points2[1][1], new_points2[1][0], mid_x, mid_y, "cyan")
    
    return bitmap



"""
    Overlay a pair of glyphs and highlight their hausdorff distances along with the
    key contributing points.
"""
def render_distance_overlay(char1, char2, bitmap1, bitmap2, points1, points2, dist1, dist2):
    red = (.96, .32, .11)
    green = (0.5, 0.72, 0)
    blue = (.05, .17, .33)
    yellow = (1.0, .71, 0)

    bitmap1 = np.dstack([bitmap1, bitmap1, bitmap1])
    bitmap2 = np.dstack([bitmap2, bitmap2, bitmap2])

    black_pixel_mask = np.all(bitmap2 == [0,0,0], axis = -1)
    bitmap2[black_pixel_mask] = blue
    black_pixel_mask = np.all(bitmap1 == [0,0,0], axis = -1)
    bitmap1[black_pixel_mask] = yellow

    new_bitmap = (bitmap1 + bitmap2)-1
    
    plt.clf() # Clears the current figure
    
    
    if points1 is not None or points2 is not None:
        #new_bitmap = np.dstack([new_bitmap, new_bitmap, new_bitmap])
            
        mid_y = int(new_bitmap.shape[0]/2)
        mid_x = int(new_bitmap.shape[1]/2)

        p1 = mpatches.Patch(color=green, label="Distance: {0:.2f}".format(dist1))
        plt.legend(handles=[p1], bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

    if points1 is not None and points2 is not None:
        d1_src_x = points1[0][0]
        d1_src_y = points1[0][1]
        d1_dest_x = points2[0][0]
        d1_dest_y = points2[0][1]
        
        d2_dest_x = points1[1][0]
        d2_dest_y = points1[1][1]
        d2_src_x = points2[1][0]
        d2_src_y = points2[1][1]
        
        dist1 = np.linalg.norm(np.array([d1_src_x, d1_src_y]) - np.array([d1_dest_x, d1_dest_y]))
        dist2 = np.linalg.norm(np.array([d2_dest_x, d2_dest_y]) - np.array([d2_src_x, d2_src_y]))
        
        if (dist1 >= dist2):
            new_bitmap[d1_src_x, d1_src_y] = red
            new_bitmap[d1_dest_x, d1_dest_y] = red
            connect_points(d1_src_x, d1_src_y, d1_dest_x, d1_dest_y, green)
        else:
            new_bitmap[d2_src_x, d2_src_y] = red
            new_bitmap[d2_dest_x, d2_dest_y] = red
            connect_points(d2_src_x, d2_src_y, d2_dest_x, d2_dest_y, green)

    return new_bitmap

"""
    Draw an arrow to draw attention to a point.
"""
def highlight_point(x, y, mid_x, mid_y, color):
    x_dir = 1 if x < mid_x else -1
    y_dir = 1 if y < mid_y else -1
    
    arr_len = 10 
    arr_head_len = 5
    arr_head_width = 5
    arr_offset = arr_len + arr_head_len
    arr_width = 2

    plt.arrow(x + arr_offset * x_dir, y + arr_offset * y_dir, (-x_dir*arr_len), (-y_dir*arr_len), color=color, alpha=0.5, width=arr_width,
                  head_width=arr_head_width, head_length=arr_head_len)

"""
    Draw an arrow to connect two points
"""
def connect_points(x1, y1, x2, y2, color):
    arr_head_len = 3
    arr_head_width = 3
    arr_width = 0.5
    
    plt.arrow(y1, x1, (y2-y1), (x2-x1), color=color, alpha=0.9, width=arr_width,
                  head_width=arr_head_width, head_length=arr_head_len, length_includes_head=True)