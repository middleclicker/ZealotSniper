import json
import math
import shutil
import os

def load_ndjson_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file.readlines():
            data.append(json.loads(line))
    return data

file_path = 'export-result.ndjson'
ndjson_data = load_ndjson_file(file_path)

storage = []
for item in ndjson_data:
	# print(json.dumps(item, indent=4))
	storage_item = {}
	filename = item["data_row"]["external_id"]
	storage_item["filename"] = filename
	storage_item["bbox"] = []
	objects = item["projects"]["cligsku3003yp072g9zlu2n48"]["labels"][0]["annotations"]["objects"]
	if len(objects) == 0:
		continue
	for obj in objects:
		storage_item["bbox"].append(obj["bounding_box"])
	storage.append(storage_item)

validation_count = math.floor(len(storage)*0.1)
cwd = os.getcwd()
print("Writing training dataset:")
for i in range(0, len(storage)-validation_count):
	# dataset/train/images
	item = storage[i]
	print("---------------------")
	print(f"Moving {item['filename']} to dataset/train/images")
	os.rename(f"{cwd}/extracted/first_batch/{item['filename']}", f"{cwd}/dataset/train/images/{item['filename']}")
	print(f"Creating label file")
	with open(f"{cwd}/dataset/train/labels/{os.path.splitext(item['filename'])[0]}.txt", 'w') as file:
		for bbox in item["bbox"]:
			x_center = float(bbox['left']) + float(bbox['width']) / 2
			y_center = float(bbox['top']) + float(bbox['height']) / 2
			width = bbox['width']
			height = bbox['height']

			# 720x375
			x_center /= 720
			y_center /= 375
			width /= 720
			height /= 375
			file.write(f"0 {x_center} {y_center} {width} {height}\n")

print("Writing validation dataset:")
for i in range(len(storage)-validation_count, len(storage)):
	# dataset/valid/images
	item = storage[i]
	print("---------------------")
	print(f"Moving {item['filename']} to dataset/valid/images")
	os.rename(f"{cwd}/extracted/first_batch/{item['filename']}", f"{cwd}/dataset/valid/images/{item['filename']}")
	print(f"Creating label file")
	with open(f"{cwd}/dataset/valid/labels/{os.path.splitext(item['filename'])[0]}.txt", 'w') as file:
		for bbox in item["bbox"]:
			x_center = float(bbox['left']) + float(bbox['width']) / 2
			y_center = float(bbox['top']) + float(bbox['height']) / 2
			width = bbox['width']
			height = bbox['height']

			# 720x375
			x_center /= 720
			y_center /= 375
			width /= 720
			height /= 375
			file.write(f"0 {x_center} {y_center} {width} {height}\n")

#print(len(storage))
#print(json.dumps(storage, indent=4))
