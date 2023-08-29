# SpecializedChatbots_vs_ChatGPT
This repository contains the code, data, and findings for a Bachelor thesis that compares specialized chatbots developed using Bag-of-Words (BoW) and BERT algorithms to ChatGPT.

## Chatbot
This folder contains the code for developing the chatbots. The main entry point is app.py, which runs on Flask and listens on http://localhost:12897/. The required libraries are listed in requirements.txt. The trained_models subfolder contains the trained model files. The db.py file initializes a database if it doesn't already exist. The chat.json file serves as the chatbot's knowledge base, where it looks up intents and returns corresponding answers.

## Compare Hyperparameters
his folder contains a Jupyter Notebook for evaluating and plotting metrics related to different hyperparameters for BoW and BERT models. Libraries can be installed using !pip install <library_name>.

## Model Training
This folder contains Jupyter Notebooks for training the models. Start by running prepare_data.ipynb, followed by train_models.ipynb.

## Expert Review
This folder contains a Jupyter Notebook that compares ChatGPT with BoW and BERT models based on expert reviews.


## Contributing
If you find any bugs or have suggestions for improvements, please open an issue or make a pull request.

## License
This project is licensed under the MIT License. See the LICENSE.md file for details.