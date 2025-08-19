from bson import ObjectId

def to_jsonable(obj):
	if isinstance(obj, ObjectId):
		return str(obj)
	if isinstance(obj, list):
		return [to_jsonable(x) for x in obj]
	if isinstance(obj, dict):
		out = {}
		for k, v in obj.items():
			if k == '_id':
				out['id'] = str(v)
			else:
				out[k] = to_jsonable(v)
		return out
	return obj 