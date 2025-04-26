import tkinter as tk
from PIL import Image, ImageTk  # Import Pillow modules
class App(tk.Tk):
   def __init__(self):
      super().__init__()
      self.title("Simple GUI with Buttons")
      self.geometry("750x600")
      self.configure(bg="lightblue")
      
      doorimage = Image.open("A:\\College stuff\\DATA AQ\\GUI\\icons\\home-door.jpg")  # Load the .jpg image
      resizeddoorimage = doorimage.resize((150, 150))  # Resize the image  
      self.icon_image1 = ImageTk.PhotoImage(resizeddoorimage)  # Convert it to a format compatible with tkinter
      # Add Button with Icon
      self.button1 = tk.Button(self, image=self.icon_image1, command=self.action1,)
      self.button1.place(x=0,y=450)  # Place the button on the window

      airconditionerimage = Image.open("A:\\College stuff\\DATA AQ\\GUI\icons\\airconditioner.jpg")
      resizedairconditionerimage = airconditionerimage.resize((150, 150))
      self.icon_image2 = ImageTk.PhotoImage(resizedairconditionerimage)
      # Add Button with Icon 
      self.button2 = tk.Button(self, image=self.icon_image2, command=self.action2,)
      self.button2.place(x=150,y=450)

      gateimage = Image.open("A:\\College stuff\\DATA AQ\\GUI\\icons\\gate.jpg")
      resizedgateimage = gateimage.resize((150, 150))
      self.icon_image3 = ImageTk.PhotoImage(resizedgateimage)
      # Add Button with Icon
      self.button3 = tk.Button(self, image=self.icon_image3, command=self.action3,)
      self.button3.place(x=300,y=450)

      garageimage = Image.open("A:\\College stuff\\DATA AQ\\GUI\\icons\\garage.jpg")
      resizedgarageimage = garageimage.resize((150, 150))
      self.icon_image4 = ImageTk.PhotoImage(resizedgarageimage)
      # Add Button with Icon
      self.button4 = tk.Button(self, image=self.icon_image4, command=self.action4,)
      self.button4.place(x=450,y=450)

      lightsimage = Image.open("A:\\College stuff\\DATA AQ\\GUI\\icons\\light.jpg")
      resizedlightsimage = lightsimage.resize((150, 150))
      self.icon_image5 = ImageTk.PhotoImage(resizedlightsimage)
        # Add Button with Icon
      self.button5 = tk.Button(self, image=self.icon_image5, command=self.action5,)
      self.button5.place(x=600,y=450)


   def action1(self):
    """Run the face recognition logic from main.py."""
    
    try:
        from main import main  # Import the main function from main.py
        main()  # Call the main function
        print("Home door opened!")
    except Exception as e:
        print(f"Error running face recognition: {e}")
   def action2(self):
        print("Air conditioner turned on!")
   def action3(self):
        print("Gate opened!")
   def action4(self):
        print("Garage door opened!")
   def action5(self):
       print("Light is on")


app = App()
app.mainloop()
