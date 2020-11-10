import datetime
import links


link = ''

def main(hrs, mins, day):

    #How many mins before class starts do you want it to start joining
    leeway = 2



    def monday():
        global link

        #8:00 - 8:10:
        if hrs == 8 and mins < 10-leeway:
            #FIXME idk the link for it yet this just sets it to an empty str
            link = links.morning

        #8:10 - 9:30
        elif hrs == 8 and mins >= 10-leeway or hrs == 9 and mins < 30-leeway:
            link = links.class_6
        
        #9:30 - 10:30
        elif hrs == 9 and mins >= 30-leeway or hrs == 10 and mins < 30-leeway:
            link = links.class_1


        #10:45 - 11:45
        elif hrs == 10 and mins >= 45-leeway or hrs == 11 and mins < 45-leeway:
            link = links.class_1


        #11:45 - 12:45
        elif hrs == 11 and mins >= 45-leeway or hrs == 12 and mins < 45-leeway: 
            link = links.class_4


        #12:45 - 1:05       
        elif hrs == 12 and mins >= 45-leeway or hrs == 13 and mins < 5-leeway:
            link = links.class_10

        #1:45 - 3:00           
        elif hrs == 13 and mins >= 45-leeway or hrs == 14 or hrs == 15:
            link = links.class_7
        
        else:
            link = ''

   
    def tuesday():

        global link

        #8:00 - 8:10:
        if hrs == 8 and mins < 10-leeway:
            #FIXME idk the link foret this just sets it to an empty str
            link = links.class_12


        #8:10 - 9:30
        elif hrs == 8 and mins >= 10-leeway or hrs == 9 and mins < 30-leeway:
            link = links.class_1

        
        #9:30 - 10:30
        elif hrs == 9 and mins >= 30-leeway or hrs == 10 and mins < 30-leeway:
            link = links.class_8

        #10:45 - 11:45
        elif hrs == 10 and mins >= 45-leeway or hrs == 11 and mins < 45-leeway:
            link = links.class_2


        else:
            link = '' 

    def wednesday():

        global link

        #8:00 - 8:10:
        if hrs == 8 and mins < 10-leeway:
            #FIXME idk the link for it yet this just sets it to an empty str
            link = links.class_12


        #8:10 - 9:30
        elif hrs == 8 and mins >= 10-leeway or hrs == 9 and mins < 30-leeway:
            link = links.class_6
        
        #9:30 - 10:30
        elif hrs == 9 and mins >= 30-leeway or hrs == 10 and mins < 30-leeway:
            link = links.class_5


        #10:45 - 11:45
        elif hrs == 10 and mins >= 45-leeway or hrs == 11 and mins < 45-leeway:
            link = links.class_5


        #11:45 - 12:45
        elif hrs == 11 and mins >= 45-leeway or hrs == 12 and mins < 45-leeway: 
            link = links.class_1

        

        #12:45 - 1:05
        elif hrs == 12 and mins >= 45-leeway or hrs == 13 and mins < 5-leeway:
            link = links.class_10

        #1:45 - 3:00
        elif hrs == 13 and mins >= 45-leeway or hrs == 14 or hrs == 15:
            pass
            # link = links.class_8

        else:
            link = '' 


    def thursday():

        global link

        #8:00 - 8:10:
        if hrs == 8 and mins < 10-leeway:
            link = links.class_12


        #8:10 - 9:30
        elif hrs == 8 and mins >= 10-leeway or hrs == 9 and mins < 30-leeway:
            link = links.class_1

        
        #9:30 - 10:30
        elif hrs == 9 and mins >= 30-leeway or hrs == 10 and mins < 30-leeway:
            link = links.class_3


        #10:45 - 11:45
        elif hrs == 10 and mins >= 45-leeway or hrs == 11 and mins < 45-leeway:
            link = links.class_3


        else:
            link = '' 

    def friday():

        global link

        #8:00 - 8:10
        if hrs == 8 and mins < 10-leeway:
            link = links.class_12


        #8:10 - 9:30
        elif hrs == 8 and mins >= 10-leeway or hrs == 9 and mins < 30-leeway :
            link = links.class_6
        
        else:
            link = '' 

    def weekday():
        #here based on which weekday it is it executes the corresponding function

        if day == 1:
            monday()
        
        elif day == 2:
            tuesday()

        elif day == 3:
            wednesday()

        elif day == 4:
            thursday()
        
        elif day == 5:
            friday()

    weekday()
