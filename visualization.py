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
    Display a pair of glyphs and their hausdorff distances, highlighting the key
    contributing points.
"""
def render_image_pair(char1, char2, bitmap1, bitmap2, points1, points2, dist1, dist2):
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

        draw_arrow(points1[0][1], points1[0][0], mid_x, mid_y, "red")
        draw_arrow(points1[1][1], points1[1][0], mid_x, mid_y, "cyan")

    if points2 is not None:
        # Adjust column of second bitmap by width of first
        new_points2 = [(p[0], p[1] + bitmap1.shape[1]) for p in points2]
        bitmap[new_points2[0][0], new_points2[0][1]] = [1, 0, 0]
        bitmap[new_points2[1][0], new_points2[1][1]] = [0, 1, 1]

        draw_arrow(new_points2[0][1], new_points2[0][0], mid_x, mid_y, "red")
        draw_arrow(new_points2[1][1], new_points2[1][0], mid_x, mid_y, "cyan")
    
    return bitmap

"""
    Draw an arrow on an image using pyplot
"""
def draw_arrow(x, y, mid_x, mid_y, color):
    x_dir = 1 if x < mid_x else -1
    y_dir = 1 if y < mid_y else -1
    
    arr_len = 10 
    arr_head_len = 5
    arr_head_width = 5
    arr_offset = arr_len + arr_head_len
    arr_width = 2

    plt.arrow(x + arr_offset * x_dir, y + arr_offset * y_dir, (-x_dir*arr_len), (-y_dir*arr_len), color=color, alpha=0.5, width=arr_width,
                  head_width=arr_head_width, head_length=arr_head_len)