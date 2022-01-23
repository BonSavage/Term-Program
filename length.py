#Bon Savage (C) 2021

import math
import numbers

#Measure units

class LengthUnit:
    def __init__(self,size):
        assert(isinstance(size,numbers.Number))
        self.__size = size

    def size(self):
        return self.__size

    def divisor(self,measure):
        return self.size()/measure.size()

NIO = LengthUnit(1)
KHUEP = LengthUnit(NIO.size()*12)
WA = LengthUnit(KHUEP.size()*8)
SEN = LengthUnit(WA.size()*20)
CENTIMETER = LengthUnit(WA.size() / 200)
METER = LengthUnit(CENTIMETER.size() * 100)
SOK = LengthUnit(CENTIMETER.size() * 50)

def rem(num,divisor):
    return num % (-divisor if num < 0 else divisor)

class Length:
    def __init__(self,units,measure):
        self.__units = units
        self.__measure = measure

    def get_units(self):
        return self.__units

    def scale_to(self,measure):
        return Length(self.get_units() * LengthUnit.divisor(self.__measure,measure),measure)

    def beyond(self,measure):
        return Length(rem(self.get_units(), LengthUnit.divisor(measure,self.__measure)),self.__measure)
        

    #Arithmetic protocol

    def add(ln1,ln2):
         return Length(ln1.get_units() + ln2.scale_to(ln1.__measure).get_units(),ln1.__measure)

    def sub(ln1,ln2):
        return Length(ln1.get_units()  - ln2.scale_to(ln1.__measure).get_units(),ln1.__measure)

    def mul(ln,n):
        return Length(ln.get_units() * n,ln.__measure)

    def div(ln,n):
        return Length(ln.get_units() / n,ln.__measure)

    #Comparison

    def lesserp(l1,l2):
    	return l1.get_units() < Length.scale_to(l2,l1.__measure).get_units()

    def equalp(l1,l2):
    	return l1.get_units() == Length.scale_to(l2,l1.__measure).get_units()

    def biggerp(l1,l2):
    	return l1.get_units() > Length.scale_to(l2,l1.__measure).get_units()

LIMIT = Length(10,SEN)

class LengthOverflow(Exception):
    pass

class ThaiLength(Length):
    def __init__(self, nio_count = 0, khuep_count = 0,wa_count = 0):
        total=nio_count+khuep_count*(KHUEP.divisor(NIO))+wa_count*(WA.divisor(NIO))
        Length.__init__(self,total,NIO)
        if (abs(total) > LIMIT.scale_to(NIO).get_units()):
            raise LengthOverflow()
        
    #Selection protocol

    def select_nios(self):
        return self.beyond(KHUEP).get_units()

    def select_khueps(self):
        return Length.sub(self.beyond(WA),self.beyond(KHUEP)).scale_to(KHUEP).get_units()

    def select_was(self):
        return Length.sub(self,self.beyond(WA)).scale_to(WA).get_units()

    #Arithmetic protocol

    def add(l1,l2):
         return ThaiLength(Length.add(l1, l2).get_units())

    def sub(l1,l2):
        return ThaiLength(Length.sub(l1, l2).get_units())

    def mul(l,n):
        return ThaiLength(Length.mul(l,n).get_units())

    def div(l,n):
        return ThaiLength(Length.div(l,n).get_units())

    def complement_to_sen(self):
        return ThaiLength(SEN.divisor(NIO) * (-1 if self.get_units() < 0 else 1) - self.get_units())
