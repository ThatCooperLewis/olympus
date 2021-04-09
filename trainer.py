import json
import random
import time

from model import Model

default_params = {
    "seq_len": 10,
    "dropout": 0.15,
    "epoch_count": 50,
    "testing_split": 0.88,
    "validation_split": 0.2
}

# reallyGoodOne
starting_params = {
    "seq_len": 22,
    "dropout": 0.1893861151446167,
    "epoch_count": 300,
    "testing_split": 0.88,
    "validation_split": 0.2
}

def randomize_params(params: dict, fixed: list) -> dict:
    if 'seq_len' not in fixed:
        params['seq_len'] = random.randint(10, 50)
    if 'dropout' not in fixed:
        params['dropout'] = round(random.uniform(.15, .3), 3)
    if 'epoch_count' not in fixed:
        params['epoch_count'] = random.randint(100, 500)
    if 'testing_split' not in fixed:
        params['testing_split'] = round(random.uniform(.85, .95), 2)
    if 'validation_split' not in fixed:
        params['validation_split'] = round(random.uniform(.15, .25), 2)
    return params

def __alter(params: dict, key: str, ignore_list: list, isInt: bool, min, max):
    if key in ignore_list: return params
    value = params[key]
    new_val = 0
    while new_val < min or new_val > max:
        new_val = value * round(random.uniform(.9, 1.1), 3)
        if isInt: new_val = round(new_val)
    params[key] = new_val
    return params

def alter_params(params: dict, fixed: list) -> dict:
    params = __alter(params, 'seq_len', fixed, True, 10, 50)
    params = __alter(params, 'dropout', fixed, False, .15, .3)
    params = __alter(params, 'epoch_count', fixed, True, 100, 500)
    params = __alter(params, 'testing_split', fixed, False, .85, .95)
    params = __alter(params, 'validation_split', fixed, False, .15, .25)
    return params

def build_and_train(params: dict):
    start = time.time()
    model = Model(model_name=str(int(start)), input_csv='bitstamp60sec.csv', params=params)
    model.train()
    model.evaluate()
    model.save_params()
    model.plot_model_loss(save=True).close()
    duration = str(time.time() - start)

    train_loss_history =  model.history.history['loss']
    validation_loss_history = model.history.history['val_loss']
    train_loss, test_loss = model.evaluate()
    results = {
        "timestamp": start,
        "duration": duration,
        "train_loss" : train_loss,
        "test_loss" : test_loss,
        "train_loss_history": train_loss_history,
        "validation_loss_history": validation_loss_history
    }

    with open(f"results/{model.name}/validation.json", "w+") as file:
        json.dump(results, file, indent=4)
    return results

def find_best_alteration(params: dict, cycles: int, randomize: bool, best_result: dict = {"test_loss" : 1}):
    best_params = params
    for i in range(cycles):
        if i > 0: 
            if randomize:
                params = randomize_params(params, ['testing_split'])
            else:
                params = alter_params(params, ['testing_split'])
        result = build_and_train(params)
        if result['test_loss'] < best_result['test_loss']:
            best_result = result
            best_params = params
    print(f"Best: {best_result['timestamp']}")
    return best_params, best_result

if __name__ == "__main__":
    best_result = {'test_loss': 0.0008506495505571365, 'timestamp': 'anotherGoodOne'}
    best_params = starting_params
    for i in range (5):
        if i > 0:
            best_params, best_result = find_best_alteration(best_params, 10, False, best_result)
        else:
            best_params, best_result = find_best_alteration(best_params, 10, True, best_result)
    print(f"Overall Best: {best_result['timestamp']}")



# Argument Ideas
# --fixed : which params to not change