import os, random, shutil

img_path = "./udacity/images/"
label_path = "./udacity/labels/"
dst_img_path="./udacity_5000/images/"
dst_label_path="./udacity_5000/labels/"

files = os.listdir(img_path)
samples = random.sample(files, 5000)
samples_name = [os.path.splitext(os.path.basename(filepath))[0] for filepath in samples]
for filename in samples_name:
	if not os.path.exists(dst_label_path):
		os.makedirs(dst_label_path)
	if not os.path.exists(dst_img_path):
		os.makedirs(dst_img_path)
	img_src = os.path.join(img_path, filename+".jpg")
	lable_src = os.path.join(label_path, filename+".txt")
	img_dst = os.path.join(dst_img_path, filename+".jpg")
	label_dst  = os.path.join(dst_label_path, filename+".txt")
	shutil.copyfile(img_src, img_dst)
	shutil.copyfile(lable_src, label_dst)
	print(filename)