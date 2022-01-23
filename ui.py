from tkinter import *
from length import *


#Wraps and composes

class LabeledString:
    def __init__(self,master,label_text,init_text = ""):
        self.__label = Label(master,text=label_text)
        self.__text = StringVar()
        self.__text.set(init_text)
        self.__entry = Entry(master,textvariable = self.__text)

    def set_pos(self,x,y):
        self.__label.grid(column=x,row=y)
        self.__entry.grid(column=x+1,row=y)

    def set_text(self,text):
        self.__text.set(text)

    def get_text(self):
        return self.__text.get()

    def disable(self):
        self.__entry.config(state=DISABLED)

    def __del__(self):
        self.__label.destroy()
        self.__entry.destroy()


class ThaiLengthView:
    def __init__(self,master,label_text,read_only=False):
        self.__label = Label(master,text = label_text)
        self.__nios = LabeledString(master,"Nios")
        self.__khueps = LabeledString(master,"Khueps")
        self.__was = LabeledString(master,"Was")
        if read_only:
            self.__nios.disable()
            self.__khueps.disable()
            self.__was.disable()

    def update(self,length):
        self.__nios.set_text(str(length.select_nios()))
        self.__khueps.set_text(str(length.select_khueps()))
        self.__was.set_text(str(length.select_was()))

    def read_length(self):
        grant_num = (lambda str : 0 if str == "" else float(str))
        return ThaiLength(grant_num(self.__nios.get_text()),grant_num(self.__khueps.get_text()),grant_num(self.__was.get_text()))

    def set_pos(self,x,y):
        self.__label.grid(column=x+1,row=y)
        self.__nios.set_pos(x,y+1)
        self.__khueps.set_pos(x,y+2)
        self.__was.set_pos(x,y+3)

    def __del__(self):
        self.__label.destroy()


#States
class EmptyState: #Just nothing!
    def __init__(self):
        pass

    def set_inactive(self):
        pass

class CalculationState(EmptyState): #Quasi abstract class
    def __init__(self,master,x,y,action):
        self.__button = Button(master,text="Calculate",command=action)
        self.__button.grid(column=x+2,row=y+2)

    def set_inactive(self):
        self.__button.destroy()

class NumberInputState(CalculationState):
    def __init__(self,master,x,y,operation,title):
        self.__input = LabeledString(master,title)
        self.__input.set_pos(x,y+2)
        CalculationState.__init__(self,master,x,y,(lambda : operation(float(self.__input.get_text()))))
    
class LengthInputState(CalculationState):
    def __init__(self,master,x,y,operation,title):
        self.__input = ThaiLengthView(master,title)
        self.__input.set_pos(x,y)
        def action():
            try:
                operation(self.__input.read_length())
            except LengthOverflow:
                pass
        CalculationState.__init__(self,master,x,y,action)

    def set_inactive(self):
        del self.__input
        CalculationState.set_inactive(self)


class ResultState(EmptyState): #String output state
    def __init__(self,master,x,y,text):
        self.__out = LabeledString(master,"Result",text)
        self.__out.set_pos(x,y+1)
        self.__out.disable()

class LengthResultState(ResultState): #Length output state
    def __init__(self,master,x,y,length):
        self.__out = ThaiLengthView(master,"Result",read_only=True)
        self.__out.set_pos(x,y)
        self.__out.update(length)

    
class TkUi:
    def __init__(self):
	    self.__win = Tk()
	    self.__win.grid_rowconfigure(0, weight=1)
	    self.__win.grid_columnconfigure(0, weight=1)
	    self.__win.resizable(False,False)
	    self.__frame = Frame(self.__win)
	    self.__frame.grid(column=0,row=0,sticky=NSEW)
	    self.__math_frame = Frame(self.__win)
	    self.__math_frame.grid(column=0,row=1,sticky=NSEW)
	    self.__convert_frame = Frame(self.__win)
	    self.__convert_frame.grid(column=1,row=1,sticky=NSEW)
	    self.__interact_frame = Frame(self.__win)
	    self.__interact_frame.grid(column=1,row=0)
	    self.__length = ThaiLength()
	    self.__length_view = ThaiLengthView(self.__frame,"Length",read_only=True)
	    self.__length_view.set_pos(0,0)
	    self.__calc_state = EmptyState()

    def update_state(self,state):
        self.__calc_state.set_inactive()
        self.__calc_state = state

    def make_operation(self,op):
        def operation(operand):
            self.update_state(EmptyState())
            self.update_length(op(operand))
        return operation

    def number_input(self,title,op):
        self.update_state(NumberInputState(self.__interact_frame,0,2,self.make_operation(op),title))

    def length_input(self,title,op):
        self.update_state(LengthInputState(self.__interact_frame,0,0,self.make_operation(op),title))

    def compare_input(self,title,op):
        self.update_state(LengthInputState(self.__interact_frame,0,0,(lambda operand : self.output(str(op(operand)))),title))

    def output(self,result):
        self.update_state(ResultState(self.__interact_frame,0,2,result))

    def length_output(self,length):
        self.update_state(LengthResultState(self.__interact_frame,0,0,length))

    def update_length(self,length):
        self.__length = length
        self.__length_view.update(length)

    def driver_loop(self):
        def add_button(title,action,x,y,frame=self.__math_frame):
            def command():
                self.update_length(self.__length)
                action()
            btn = Button(frame,text=title,command=command)
            btn.grid(column=x,row=y)

        def safe_div(n):
            try:
                return self.__length.div(n)
            except ZeroDivisionError:
                self.output("NaN")
                return self.__length

        def compare(len1,len2):
            if (len1.biggerp(len2)):
                return "Bigger"
            elif (len1.equalp(len2)):
                return "Equal"
            else: return "Lesser"

        def arithmetic(f):
            def res(arg):
                try:
                    return f(arg)
                except LengthOverflow:
                    self.output("Value is too big")
                    return self.__length
            return res

        def clear():
            self.update_length(ThaiLength(0,0,0))
            self.update_state(EmptyState())

        add_button("+",(lambda : self.length_input("Addition",arithmetic(self.__length.add))),0,0)
        add_button("*",(lambda : self.number_input("Multiplication",arithmetic(self.__length.mul))),0,1)
        add_button("-",(lambda : self.length_input("Subtraction",arithmetic(self.__length.sub))),1,0)
        add_button("/",(lambda : self.number_input("Division",arithmetic(safe_div))),1,1)
        #add_button(">",(lambda : self.compare_input("Large?",self.__length.biggerp)),2,0)
        #add_button("<",(lambda : self.compare_input("Smaller?",self.__length.lesserp)),3,0)
        #add_button("=",(lambda : self.compare_input("Equal?",self.__length.equalp)),4,0)
        add_button("Compare",(lambda : self.compare_input("Comparison",(lambda ln : compare(self.__length,ln)))),2,0)
        add_button("Clear",clear,2,1)
        add_button("To meters",(lambda : self.output(str(math.trunc(self.__length.scale_to(METER).get_units())) + " meters")),1,0,self.__convert_frame)
        add_button("To centimeters",(lambda : self.output(str(math.trunc(self.__length.scale_to(CENTIMETER).get_units())) + " centimeters")), 1,1,self.__convert_frame)
        add_button("To soks",(lambda : self.output(str(math.trunc(self.__length.scale_to(SOK).get_units())) + " soks")), 1,2,self.__convert_frame)
        add_button("Complement to sen", (lambda: self.length_output(self.__length.complement_to_sen())),0,0,self.__convert_frame)
        
        self.__win.mainloop()
