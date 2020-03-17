
import cv2
import numpy as np
import math
from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk


filetypes = [('image_file', ('*.jpg', '*.jpeg', '*.png')),('all_files', '*')]


def diff(x, y):
    if x > y:
        return x-y
    else:
        return y-x


def process(origin1,origin):
    global mid
    # 灰度处理
    gray_img1 = cv2.cvtColor(origin1, cv2.COLOR_BGR2GRAY)
    gray_img1 = cv2.blur(gray_img1, (5, 5))
    gray = cv2.cvtColor(origin1, cv2.COLOR_BGR2GRAY)
    global k
    k = np.ones([5, 5])
    k = k * 30
    gray = cv2.erode(gray, kernel=k)
    gray = cv2.dilate(gray, kernel=k) - cv2.erode(gray, kernel=k)

    gary = cv2.medianBlur(gray, 3, gray)
    # cv2.imshow("gray", gray)
    # gray = cv2.Canny(gray, 80, 160)
    # gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    pale = Label(root, text="")
    pale.place(relx=0.001, rely=0.45, relwidth=0.4, relheight=0.8)
    mid = origin1
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    f=1.0
    h, w, ch = origin.shape
    result = np.zeros((h, w, ch), dtype=np.uint8)
    for cnt in range(len(contours)):
        cv2.drawContours(result, contours, cnt, (0, 255, 0), 10)
        # 轮廓逼近
        epsilon = 0.05 * cv2.arcLength(contours[cnt], True)
        approx = cv2.approxPolyDP(contours[cnt], epsilon, True)
        # 分析几何形状
        corners = len(approx)
        shape_type = ""
        if True:
            mm = cv2.moments(contours[cnt])
            if mm['m00'] == 0:
                continue
            cx = int(mm['m10'] / mm['m00'])
            cy = int(mm['m01'] / mm['m00'])
            if mm['m00'] > 800:
                x, y, w, h = cv2.boundingRect(contours[cnt])

                rect = cv2.minAreaRect(contours[cnt])
                c = cv2.minEnclosingCircle(contours[cnt])
                s = rect[1][0] / rect[1][1]
                if s > 1.2 or s < 0.8:
                    if math.pow((c[0][0] - (rect[0][0] + rect[1][0]) / 2), 2) + math.pow(
                            (c[0][1] - (rect[0][1] + rect[1][1]) / 2), 2) <= c[1] * c[1]:
                        continue
                    box = cv2.boxPoints(rect)
                    box = np.int0(box)
                    cv2.circle(origin, (cx, cy), 2, (0, 0, 255), -1)
                    cv2.drawContours(origin, [box], 0, (0, 0, 255), 2)
                    print("%d,%d" % (cx, cy))

                    zuo = '%d, %d' % (cx,cy)
                    ce = Label(root, text=zuo)

                    ce.place(relx=0.23, rely=0.4+f*0.05)
                    f = f + 1.0


    circles = cv2.HoughCircles(gray_img1, cv2.HOUGH_GRADIENT, 1, 0.1, param1=30, param2=60, minRadius=50, maxRadius=150)
    # 转化整数
    circles = np.uint16(np.around(circles))

    circles_data = [[circles[0][0]]]

    for i in circles[0, :]:
        # 勾画圆形，planets图像、(i[0],i[1])圆心坐标，i[2]是半径
        cv2.circle(mid, (i[0], i[1]), i[2], (0, 255, 0), 1)
        # 勾画圆心，圆心实质也是一个半径为2的圆形
        cv2.circle(mid, (i[0], i[1]), 2, (0, 0, 255), 3)

        flag = 0
        for j in range(0, len(circles_data)):
            for k in range(0, len(circles_data[j])):
                _diff = diff(circles_data[j][0][0], i[0]) + diff(circles_data[j][0][1], i[1])
                if _diff <= 80:
                    flag = 1
                    circles_data[j].append(i)
                    break
            if flag == 1:
                break
        if flag == 0:
            circles_data.append([i])

    b=1.0
    c=1.0
    # 区分正反，并标记
    for i in circles_data:
        cv2.circle(origin, (i[0][0], i[0][1]), i[0][2], (0, 255, 0), 2)
        cv2.circle(origin, (i[0][0], i[0][1]), 2, (0, 0, 255), 3)

        x_offset = abs(origin.shape[1] / 2 - i[0][0])
        y_offset = abs(origin.shape[0] / 2 - i[0][1])
        r = i[0][2]
        distance = pow(pow(x_offset, 2) + pow(y_offset, 2), 1 / 2)
        _ratio = r / distance * 2

        # 区分阈值

        if len(i) < 100 * _ratio:
            cv2.putText(origin, "Front", (i[0][0], i[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            coordinate = '%d, %d' % (i[0][0],i[0][1])
            a = Label(root,text=coordinate)
            a.place(relx=0.05,rely = b*0.05+0.4)
            b = b + 1.0

            print(i[0][0], i[0][1], ",r", i[0][2], x_offset, y_offset, ",num:", len(i), ",distance:", distance,
                  ",ratio:", 100 * _ratio, ",front")
        else:
            cv2.putText(origin, "Back", (i[0][0], i[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            coordinate = '%d, %d' % (i[0][0], i[0][1])
            a = Label(root, text=coordinate)
            a.place(relx=0.14, rely=c * 0.05 + 0.4)
            c= c+1.0
            print(i[0][0], i[0][1], ",r", i[0][2], x_offset, y_offset, ",num:", len(i), ",distance:", distance,
                  ",ratio:", 100 * _ratio, ",back")


    # for i in circles_data:
    #    print(i[0][0], i[0][1], i[0][2], len(i))

    return origin


def show():
    im = Image.open("result1.jpg")
    img = ImageTk.PhotoImage(im)
    imLabel = Label(root, image=img)
    imLabel.place(x=0.2, y=0.2)

def displayOrigin():
    global fp
    fp = filedialog.askopenfilename(title = 'open', filetypes = filetypes)
    img = Image.open(fp)
    print(img.size)
    img = img.resize((640, 480))
    img = ImageTk.PhotoImage(img)
    imLabel = Label(root, image=img)
    imLabel.image = img
    imLabel.place(relx=0.4, rely=0.1)



def detec():
    string = fp
    string = string.replace('/','\\\\')
    print(string)
    pic1 = cv2.imread(string)
    pic2 = cv2.imread(string)
    pic = process(pic1,pic2)
    cv2.imwrite("1.jpg", pic)
    img = Image.open("1.jpg")
    img = img.resize((640,480))
    img = ImageTk.PhotoImage(img)
    imLabel = Label(root, image=img)
    imLabel.image = img
    imLabel.place(relx=0.4,rely=0.1)
    #for i in circles[0, :]:
    #    coordinate = "(%d,%d)" %(i[0],i[1])
    #    print(coordinate)

root = Tk()

root.title('test')
#w = root.winfo_screenwidth()
#h = root.winfo_screenheight()
#root.geometry('%dx%d'%(w,h))
root.state("zoomed")  #仅windows可用

readim = Button(root,text='open an img',font = ("Times", 18),command=displayOrigin)
readim.place(relx=0.1,rely=0.1,relwidth=0.15,relheight=0.09)

bt = Button(root,text='detect',font = ("Times", 18),command=detec)
bt.place(relx=0.1,rely=0.25,relwidth=0.15,relheight=0.09)

zz = Label(root,text='正向瓶盖',font = ("Times", 18))
zz.place(relx=0.02,rely=0.4,relwidth=0.1)

ff = Label(root,text='反向瓶盖',font = ("Times", 18))
ff.place(relx=0.11,rely=0.4,relwidth=0.1)

cc=Label(root,text='侧向瓶盖',font = ("Times", 18))
cc.place(relx=0.2,rely=0.4,relwidth=0.1)

root.mainloop()