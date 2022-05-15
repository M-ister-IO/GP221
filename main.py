""""created by Charles DESCAMPS | Anouk VITIS | Irvin PETIT
Napping robot scan it's envyronment by travelling a rectancgle then save a file with a PNG map and a csv file

"""
import time
import os
import csv
from easygopigo3 import EasyGoPiGo3

"""Napping brain"""

gpg = EasyGoPiGo3()
dist_sens = gpg.init_distance_sensor()
servo = gpg.init_servo()
servo.rotate_servo(90)
dist_sens=gpg.init_distance_sensor()

# Green=(0,255,0)
# Orange=(255,80,0)
# Yellow=(255,255,0)
# Blue=(0,0,255)

#To avoid probleems with the sensor
# def drive(dis):
#     dis-=200
#     gpg.drive_cm(int(dis/10),blocking=False)
def aqdist():
    L=[]
    for i in range(10):
        d=dist_sens.read_mm()
        L.append(d)
    time.sleep(0.25)
    L.append(dist_sens.read_mm())
    L.sort()
    if L[0]>=2000: #due to sensor trouble with the height of detection we set a "limit min sensor" else we cut the trajectory in part.
        L[0]=1000
    print(L)
    return int(L[0]) #take the lowest value to be sure it doesn't hit the wall
    

v=173.2 # input the velocity of the robot
i=0




regard=[[],[],[],[]]
parcouru=[0,0,0,0]  
trajet=[[20],[],[],[]] 
peri=[0,0,0,0] 
reste=[0,0,0,0]

y=0 #represent the section of one side
while i<4:
    time.sleep(0.5)
    
    d=aqdist()
    # gpg.set_left_eye_color((int(255-0.085*d),int(0.085*d),0))
    # gpg.open_left_eye()
    print('distance to run in side: ', i)
    print(d, "before verif")
    if d>=240:
        d=d-40#we had a -40mm to be sure it doesnt hit the wall. We don't want Napping to get hurt
        trajet[i].append(d) 
    else:
        peri[i]+=d
        reste[i]=d
        d=0
    
   
    parcouru[i]+=d
    peri[i]+=d
    print(d)
    if d>=200:
        t_end=time.time()+int(d/v)
        l=[]
        regard[i].append(l)
        servo.rotate_servo(5)
        t0=time.time()

        
        gpg.forward()
        gpg.steer(29.7,100)
        while time.time()< t_end:
            do=dist_sens.read_mm()
            gpg.set_right_eye_color((int(255-0.085*do),0,int(0.085*do)))
            gpg.open_right_eye()
            
            #too much light mission aboared
            
            # gpg.set_left_eye_color((int(d/255*(time.time()-t0)),int(255-d/255*(time.time()-t0)),0))
            # gpg.open_left_eye() 

            regard[i][y].append([do,time.time()-t0,y])
            
        y+=1
        gpg.stop()
        gpg.close_right_eye()
        gpg.close_left_eye()
        servo.rotate_servo(90)
        
        

    else:
        gpg.turn_degrees(91)
        i+=1
        y=0

"""Data analysis"""

# print(regard)
# print(parcouru)
# print(trajet)
# print(peri)
# print(reste)

from PIL import Image

#result of 3 peoples working with differents variables names :(
distances=peri
speed=v  #mm/s set earlier

for i in range(len(regard)):
    for j in range(len(regard[i])):

            if j==0:
                pass
            else:
                for k in range(len(regard[i][j])):
                    regard[i][j][k][1]+=regard[i][j-1][-1][1]


sequence=[[],[],[],[]]

for i in range(len(sequence)):
    for j in range(len(regard[i])):
        for k in range(len(regard[i][j])):
            sequence[i].append(regard[i][j][k])



coef=10 #we converted the mm in cm
width=int(distances[2]/coef)+1
height=int(distances[1]/coef)+1
obstacle=[[],[],[],[]]
# origine=[0,0]



img =Image.new(mode='RGB',size=(width,height),color=(0,0,0))


pixels=img.load()

for i in range(len(sequence)):
    for j in range(len(sequence[i])):
        sequence[i][j][1] = speed * sequence[i][j][1] / coef
        sequence[i][j][0] = sequence[i][j][0] / coef


        if int(sequence[i][j][1]+23+reste[2]/coef)>width or (sequence[i][j][0])>height:
            pass
        else:
            try:
                if i==0: #rouge
                    x=int(sequence[i][j][1]+23-reste[0]/coef)
                    y=int(sequence[i][j][0])
    
                    pixels[x,y]=(255,0,0)
                    obstacle.append([x,y,i])
    
                if i==1:  #vert
                    x=int(int(distances[i-1]/coef)-sequence[i][j][0]+23-reste[0]/coef)
                    y=int(sequence[i][j][1])+13
    
                    pixels[x,y] = (0, 255, 0)
                    obstacle.append([x,y,i])
    
                if i==2:#bleu
    
                    x=int(int(distances[i]/coef)-sequence[i][j][1]-13-23-reste[0]/coef)
                    y=int(int(distances[i-1]/coef)-sequence[i][j][0]-13-reste[1]/coef)
    
                    pixels[x,y] = (0, 0, 255)
                    obstacle.append([x,y,i])
    
    
    
                if i==3: #blanc
    
                    x=int(sequence[i][j][0]+13+reste[2]/coef)
                    y=int(int(distances[i]/coef)-sequence[i][j][1]-23-reste[1]/coef-reste[-1]/coef)
                    obstacle.append([x,y,i])
    
    
                    pixels[x,y] = (255, 255, 255)
                    obstacle.append([x,y,i])
            except:
                pass



# img.show()


name=time.strftime("%Y_%m_%d_%H_%M_%S")

folder_name = 'documents_' + name
os.mkdir(folder_name)


info=[]

#In a futur code we could only use the obstacle in x,y coordinates and the perimeter but "more info the better" Charles
sequence_2=sequence.copy()
info.append(sequence_2)
info.append(obstacle)
info.append(parcouru)
info.append(trajet)
info.append(peri)
info.append(reste)



row_list = info

with open(folder_name+'/sequence.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(row_list)
img.save(folder_name+'/carte.png', 'png')


