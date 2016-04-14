import pymongo
from edit import editDistance, similarityMetric

def findProduct(query):
	client = pymongo.MongoClient('mongodb://<user>:<password>@ds023570.mlab.com:23570/dialog_system')
	db = client.dialog_system

	f = open("properties.txt", 'r')

	productNameList = []

	propertyList = f.read().split('\n')
	propertyList = propertyList[:-1]

	categories = ["tv", "mobiles", "laptops", "cameras", "ac", "fridges"]

	brandList = ['apple', 'hp', 'lenovo', 'lg', 'micromax', 'samsung', 'sony', "nikon", "canon", "panasonic"]


	###############################
	# Mobile 		--> 'm'		  #
	# Televisions 	--> 't'       #
	# Laptops 		--> 'l' 	  #
	# Cameras 		--> 'c' 	  #
	# Fridges 		--> 'f' 	  #
	# ACs 	 		--> 'a' 	  #
	###############################

	for cat in categories:
		for product in db[cat].find():
			productNameList.append((product["brand"].encode('utf-8').lower(), product["model name"].encode('utf-8').lower(), cat[0].lower()))

	query = query.lower().split(',')
	query = [q.strip() for q in query]
	product_brand = ""

	if (len(query) < 2):
		query = query[0].split(" ")
		hashmap = [0]*len(query)
		stopwords_ptr = open("stop_words.txt", 'r')
		stop_words = stopwords_ptr.read().split('\n')
		stop_words = stop_words[:-1]
		idx = 0
		for term in query:
			if (term in stop_words):
				hashmap[idx] = 1
			idx += 1	

		first_stop = -1
		for i in xrange(len(query), 0, -1):
			if (hashmap[i-1] and first_stop == -1):
				product_name = query[i:]
				product_name = " ".join(product_name)
				first_stop = i-1
			elif (hashmap[i-1] and first_stop != -1):
				property_name = query[i:first_stop]
				property_name = " ".join(property_name)
				break
	elif (len(query) == 2):
		product_name = query[0]
		property_name = query[1]
	else:
		return "QUERY SYNTAX ERROR, REQUIRED: [PRODUCT NAME], [PROPERTY]"

	product_name = product_name.strip(' ?!.')
	product_terms = product_name.split(" ")

	min_score = 99999
	idx = -1
	count = 0
	for term in product_terms:
		for brand in brandList:
			score = editDistance(term, brand)
			if (score < min_score):
				idx = count
				min_score = score
				product_brand = brand
		count += 1

	product_terms[idx] = product_brand
	product_name = ' '.join(product_terms)

	temp_products = []
	temp_prop = []

	for product in productNameList:
		if (product[0] == product_brand):
			score = editDistance(product[0] + " " + product[1], product_name)
			metric2 = similarityMetric(product[0] + " " + product[1], product_name)
			final_metric = (score * metric2 * 2) / (score + metric2)
			temp_products.append((product[1], product[2], final_metric))

	temp_products.sort(key=lambda tup: tup[2]) 
	temp_products = temp_products[:10]

	for prop in propertyList:
		score = editDistance(prop, property_name)
		metric2 = similarityMetric(prop, property_name)
		final_metric = (score * metric2 * 2) / (score + metric2)
		temp_prop.append((prop, final_metric))

	temp_prop.sort(key=lambda tup: tup[1]) 
	temp_prop = temp_prop[0][0]

	# temp_prop = temp_prop.replace(" ", "")
	outputs = []
	for product in temp_products:
		if (product[1] == 'm'):
			results = db.mobiles.find({"_id": product[0]})[0]
			# results = session.execute(("select %s from mobiles where modelname = '%s' ") % ( temp_prop , product[0]))[0]
		elif (product[1] == 'l'):
			results = session.execute(("select %s from laptops where modelname = '%s' ") % ( temp_prop , product[0]))[0]
		elif (product[1] == 't'):
			results = session.execute(("select %s from television where modelname = '%s' ") % ( temp_prop , product[0]))[0]
		outputs.append((product_brand.capitalize() + " " + product[0].capitalize() + ": " + results[temp_prop].capitalize()).encode('utf-8'))

	return outputs
