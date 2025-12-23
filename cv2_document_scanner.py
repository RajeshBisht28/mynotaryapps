################################
### Initiated by Rajesh Bisht 
### version : 1.0.0
### @Detect id card contours , basics...
### librar: python-cv2
### filename: cv2_document_scanner
#################################

import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils
from imutils.perspective import four_point_transform

class LeafletDocumentScanner:
    def __init__(self, image_path, final_image_path):
        self.image_path = image_path
        self.final_image_path = final_image_path

    ##### main function ################
    def __document_scanner(self, image):
        img_re,size = resizer(image)
        detail = cv2.detailEnhance(img_re,sigma_s = 20, sigma_r = 0.15)
        gray = cv2.cvtColor(detail,cv2.COLOR_BGR2GRAY) # GRAYSCALE IMAGE
        blur = cv2.GaussianBlur(gray,(5,5),0)
        # edge detect
        edge_image = cv2.Canny(blur,75,200)
        # morphological transform
        kernel = np.ones((5,5),np.uint8)
        dilate = cv2.dilate(edge_image,kernel,iterations=1)
        closing = cv2.morphologyEx(dilate,cv2.MORPH_CLOSE,kernel)

        # find the contours
        contours , hire = cv2.findContours(closing,
                                        cv2.RETR_LIST,
                                        cv2.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for contour in contours:
            peri = cv2.arcLength(contour,True)
            approx = cv2.approxPolyDP(contour,0.02*peri, True)

            if len(approx) == 4:
                four_points = np.squeeze(approx)
                break

        cv2.drawContours(img_re,[four_points],-1,(0,255,0),3)

        # find four points for original image
        multiplier = image.shape[1] / size[0]
        four_points_orig = four_points * multiplier
        four_points_orig = four_points_orig.astype(int)

        wrap_image = four_point_transform(image,four_points_orig)
        
        return wrap_image, four_points_orig, img_re, closing

############ end main function ##################
    
    def processing(self):
        #image_path=self.image_path
        final_image_path = self.final_image_path
        try:
            img_orig = cv2.imread(self.image_path)
            wrpimg, points, cnt_img, edgeimg = self.__document_scanner(img_orig)
            cv2.imwrite(final_image_path, wrpimg)
            return {
                'status': True,
                'image_path': final_image_path,
                'message': "success"
            }
        except Exception as e:
            return {
                'status': False,
                'image_path': final_image_path,
                'message': str(e)
            }

########################### Debug functions #####################

def load_image(image_path):
    img_orig = cv2.imread(image_path)
    return img_orig

def show_image(img_data, label_name):
    cv2.namedWindow(label_name,cv2.WINDOW_NORMAL)
    cv2.imshow(label_name, img_data)
    

def flush_all():
    cv2.waitKey()
    cv2.destroyAllWindows()

######### Helper functions #################
def resizer(image,width=500):
    # get widht and height
    h,w,c = image.shape
    
    height = int((h/w)* width )
    size = (width,height)
    image = cv2.resize(image,(width,height))
    return image, size


if __name__ == "__main__":
    print("oooo...")
    image_path = r"F:\eNotaryApp\bbb.jpg"
    result_path = r"F:\eNotaryApp\XXXX_bbb.jpg"
    obj_docscan = LeafletDocumentScanner(image_path, result_path)
    res = obj_docscan.processing()
    print("=reslt===")
    print(res)

    """ img_orig = load_image(image_path)

    wrpimg, points, cnt_img, edgeimg = document_scanner(img_orig)
    cv2.imwrite('original.jpg',img_orig)
    cv2.imwrite('resize.jpg',cnt_img)
    cv2.imwrite('edge.jpg',edgeimg)
    cv2.imwrite('wrap.jpg',wrpimg)

    cv2.imshow('original',img_orig)
    cv2.imshow('resize',cnt_img)
    cv2.imshow('edge',edgeimg)
    cv2.imshow('wrap',wrpimg)
    cv2.waitKey()
    cv2.destroyAllWindows() """

