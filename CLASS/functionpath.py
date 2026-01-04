class OddEven():
    def OddEven():
        NUM=int(input("Enter a number:"))
        if((NUM%2)==0):
            print(NUM,"is Even number ")
        else:
            print(NUM,"is Odd number ")

class SubfieldsInAI():
    def Subfields():
        print("Sub-fields in AI are:")
        List=['Machine Learning', 'Neural Networks', 'Vision', 'Robotics', 'Speech Processing', 'Natural Language Processing']
        for temp in List:
            print(temp)


class triangleFm():
    def triangle(): 
        Height=int(input("Height:"))
        Breadth=int(input("Breadth:"))
        Area=(Height*Breadth)/2
        
        print("Area formula:(Height*Breadth)/2")
        print("Area of Triangle:",Area)
        
        Height1=int(input("Height1:"))
        Height2=int(input("Height2:"))
        Breadth1=int(input("Breadth1:"))
        Perimeter=Height1+Height2+Breadth1
    
        print("Perimeter formula: Height1+Height2+Breadth ")
        print("Perimeter of Triangle:",Perimeter)


class ElegiblityForMarriage():
    def Elegible():
        gender=input("Your Gender:")
        age=int(input("Your Age:"))
        if(gender=='Male'):
          if(age >=21):
            print('ELIGIBLE')
          else:
            print('NOT ELIGIBLE')
        elif(gender=='Female'):
          if(age >18):
            print('ELIGIBLE')
          else:
            print('NOT ELIGIBLE')
        else:
          print('INVALID')

class tenthresult():
    def tenthmark():
        Subject1=int(input("Subject1=")) 
        Subject2=int(input("Subject2=")) 
        Subject3=int(input("Subject3=")) 
        Subject4=int(input("Subject4=")) 
        Subject5=int(input("Subject5=")) 
        add=Subject1+Subject2+Subject3+Subject4+Subject5
        Percentage=(add/5)
        print("Total :",add,)
        print("Percentage :",Percentage)
            
    