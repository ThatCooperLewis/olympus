import json
import random
import time

from main import Model
# testA = Model("modelA", input_csv='bitstamp30sec.csv')
# testA.train(seq_len=25, dropout=0.25, epochs=25, testing_split=0.95, validation_split=0.5)
# testA.save()



starting_params = {
    "seq_len": 10,
    "dropout": 0.15,
    "epoch_count": 30,
    "testing_split": 0.9,
    "validation_split": 0.3
}

def randomize(params: dict) -> dict:
    params['seq_len'] = random.randint(10, 50)
    params['dropout'] = round(random.uniform(.15, .25), 3)
    params['epoch_count'] = random.randint(3, 7)
    params['testing_split'] = round(random.uniform(.85, .95), 2)
    params['validation_split'] = round(random.uniform(.15, .25), 2)
    return params

# TODO: Extract rows from data properly
validation = [
    57606.36,
    57585.08,
    57583.55,
    57590.11,
    57592.01
]


new_params = randomize(starting_params)
startTime = time.time()
model = Model("randomTest2", input_csv='bitstamp30sec.csv', params=new_params)
model.train()
model.save()
model.plot_model_loss(save=True)
prediction = model.build_predictions(len(validation))
duration = str(time.time() - startTime)
print("Done")
print(f"Last Known: {validation}")
print(f"All Predictions: {prediction}")
print(f"Duration: {duration}")
with open(f"results/{model.name}/validation.json", "w+") as file:
    json.dump({
        "real": str(validation),
        "predicted": str(prediction),
        "duration": duration 
    }, file)