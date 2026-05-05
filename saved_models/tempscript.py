import pickle
import xgboost as xgb

old_model = pickle.load(open("leukimia_model.sav", "rb"))

old_model.save_model("leukemia_model.json")