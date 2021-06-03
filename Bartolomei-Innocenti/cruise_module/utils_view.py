import numpy as np
import cv2 as cv

def lu2lb(x,y, size):
    return int(x), int(size-y)

def show_calibration(xy, minX, maxX, scaleFactor, shiftFactor):
    minY, maxY = scaleFactor * minX + shiftFactor, scaleFactor * maxX + shiftFactor

    img_size = 800
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    
    oX, oY = (20, 100)
    #dScaleX, dScaleY = ((img_size-oX)/(maxX), (img_size-oY)/(maxY))
    dScaleX, dScaleY = (2.5,(img_size-oY)/(maxY-minY))

    cv.line(img, lu2lb(0, oY, img_size), lu2lb(img_size, oY, img_size), (255,255,255), 1)
    cv.line(img, lu2lb(oX, 0, img_size), lu2lb(oX, img_size, img_size), (255,255,255), 1)

    text = "ScaleFactor: %1.5f, ShiftFactor: %1.5f" % (scaleFactor, shiftFactor)
    cv.putText(img, text, (150, 50), cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)

    text = "%3.3f" % minX
    cv.putText(img, text, lu2lb(oX+minX*dScaleX, oY-10, img_size), cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)
    cv.circle(img, lu2lb(oX+minX*dScaleX, oY, img_size), 2, (255,255,255), 2)

    text = "%3.3f" % maxX
    cv.putText(img, text, lu2lb(oX+maxX*dScaleX, oY-10, img_size), cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)
    cv.circle(img, lu2lb(oX+maxX*dScaleX, oY, img_size), 2, (255,255,255), 2)

    text = "%3.3f" % minY
    cv.putText(img, text, lu2lb(oX-20, oY+minY*dScaleY, img_size), cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)
    cv.circle(img, lu2lb(oX, oY+minY*dScaleY, img_size), 2, (255,255,255), 2)

    text = "%3.3f" % maxY
    cv.putText(img, text, lu2lb(oX-20, oY+maxY*dScaleY, img_size), cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, 8)
    cv.circle(img, lu2lb(oX, oY+maxY*dScaleY, img_size), 2, (255,255,255), 2)
   
    for x,y in xy:
        x,y = lu2lb((x*dScaleX+oX), (y*dScaleY+oY), img_size)
        cv.circle(img, (x, y), 2, (0,255,255), 1)

    line_start = lu2lb((oX+minX*dScaleX), (oY+minY*dScaleY), img_size)
    line_end = lu2lb((oX+maxX*dScaleX), (oY+maxY*dScaleY), img_size)
    cv.line(img, line_start, line_end, (255, 255, 0), 1)

    cv.imshow('Calibration', img)
    cv.waitKey(5)
