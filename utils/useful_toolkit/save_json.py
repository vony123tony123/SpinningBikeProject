import json
import time
import numpy as np

left_line_range = [ 1815, 1051, 1874, 1076 ]
right_line_range= [0, 764, 55, 768 ]
direction = "Left"
angle = -28.7
objects = np.array([296, 596, 592, 398]).flatten().tolist()

arr = []
j=0
for i in range(3600*60):
	dict_input = {'id':j,'direction':direction, 'angle':angle, 'left_line_range':left_line_range, 'right_line_range':right_line_range,'objects':objects}
	arr.append(dict_input)
	del dict_input
	j+=1

i =0
with open("test.json", 'w') as file:
		json_input = json.dumps(arr,indent=4)
		file.write(json_input)
		del json_input

