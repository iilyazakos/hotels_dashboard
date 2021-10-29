import os
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import kaggle

# os.environ['KAGGLE_USERNAME'] = "ilyazakos"

# os.environ['KAGGLE_KEY'] = "65b0d2bf5b03108f687c0d54e63c78a1"
# os.system('kaggle competitions download -d "jessemostipak/hotel-booking-demand"')

# !kaggle competitions download -c dogs-vs-cats-redux-kernels-edition

KAGGLE_USERNAME = "ilyazakos"
KAGGLE_KEY = "65b0d2bf5b03108f687c0d54e63c78a1"

# api = KaggleApi(KAGGLE_KEY)
# api.authenticate(KAGGLE_USERNAME)



hotels = pd.read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2020/2020-02-11/hotels.csv')

print(hotels.head(5))

# api.dataset_download_files('jessemostipak/hotel-booking-demand')


# "username":"ilyazakos","key":"65b0d2bf5b03108f687c0d54e63c78a1"

# kaggle datasets download -d jessemostipak/hotel-booking-demand