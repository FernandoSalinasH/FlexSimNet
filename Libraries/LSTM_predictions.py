# Multi-step Long short-term memory to predict irradiance and temperature

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from numpy import split
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
     
data = pd.read_csv(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\temp_irradiance.csv")
dates = pd.date_range(start='2020-01-02', end='2022-01-01', freq='H')[1:]

# Choose target
target = 'temperature' # 'GHI' 'temperature'
date_split = '2021-12-01'
n_out = 1
n_input = 24 # temperature: 24, GHI: 1
verbose, epochs, batch_size  = 1, 100, 24 # 

# Load data and split into train and test
data = pd.DataFrame({target: data[target].values}, index=dates)
train_df = data.loc[data.index <= date_split ]
test_df = data.loc[data.index > date_split]
train = train_df[target].values
test = test_df[target].values

# Normalize the data
scaler = MinMaxScaler()

# convert history into inputs and outputs
# flatten data
test_aux = np.append(train[-n_input:], test) if target == 'temperature' else test
test_flat = test_aux.reshape((len(test_aux), 1))
X_test = list()
in_start = 0
# step over the entire history one time step at a time
for _ in range(len(test_flat)):
    # define the end of the input sequence
    in_end = in_start + n_input
    out_end = in_end + n_out
    # ensure we have enough data for this instance
    count = len(test_flat) if target == 'temperature' else len(test_flat) + 1
    if out_end <= count:
        x_test_input = test_flat[in_start:in_end, 0]
        x_test_input = x_test_input.reshape((len(x_test_input), 1))
        X_test.append(x_test_input)
    # move along one time step
    in_start += 1
X_test = np.array(X_test)

# convert history into inputs and outputs
# flatten data
future_data = data.loc[(data.index > '2020-01-02') & (data.index <= '2020-02-02')]
future_data = future_data[target].values
future_data = np.append(test[-n_input:], future_data)
future_flat = future_data.reshape((len(future_data), 1))
X_fut = list()
in_start = 0
# step over the entire history one time step at a time
for _ in range(len(future_flat)):
    # define the end of the input sequence
    in_end = in_start + n_input
    out_end = in_end + n_out
    # ensure we have enough data for this instance
    if out_end <= len(future_flat):
        x_fut = future_flat[in_start:in_end, 0]
        x_fut = x_fut.reshape((len(x_fut), 1))
        X_fut.append(x_fut)
    # move along one time step
    in_start += 1
X_fut = np.array(X_fut)

# convert history into inputs and outputs
# flatten data
data_flat = train.reshape((len(train), 1))
X, y = list(), list()
in_start = 0
# step over the entire history one time step at a time
for _ in range(len(data_flat)):
    # define the end of the input sequence
    in_end = in_start + n_input
    out_end = in_end + n_out
    # ensure we have enough data for this instance
    if out_end <= len(data_flat):
        x_input = data_flat[in_start:in_end, 0]
        x_input = x_input.reshape((len(x_input), 1))
        X.append(x_input)
        y.append(data_flat[in_end:out_end, 0])
    # move along one time step
    in_start += 1
X = np.array(X)
y = np.array(y)

# Create the LSTM model
model = Sequential()
# Add LSTM layers with dropout
model.add(LSTM(units=200, activation='relu', input_shape=(n_input, 1), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=100, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(100, activation='relu'))
model.add(Dense(n_out))
model.compile(optimizer='adam', loss='mse')
model.summary()

# Train the model
history = model.fit(
    X, y,
    epochs= epochs,
    batch_size= batch_size,
    verbose=verbose,
    validation_split=0.2,  # Use part of the training data as validation
)

# # Make predictions from test data directly
# prediction_sequence = model.predict(X_test, verbose=1)
# predictions = np.array(prediction_sequence)
# predictions = predictions.ravel()

# Make predictions NO updating the sequence with previous predictions in test set
predictions = []
# sequence = X[-n_input, :].reshape((1, n_input, 1))  # Get the last sequence hours of the training data
for i in range(len(X_test)):
    sequence = X_test[i, :].reshape((1, n_input, 1))
    # predict the week
    prediction_sequence = model.predict(sequence, verbose=0)
    prediction_sequence = np.around(prediction_sequence, 2)
    # store the predictions
    predictions.append(prediction_sequence)
# evaluate predictions days for each week
predictions = np.array(predictions)
predictions = np.where((predictions < 3) & (target == 'GHI'), 0, predictions)
predictions = predictions.ravel()

# # Make predictions updating the sequence with previous predictions
# predictions = []
# sequence = train[-n_input:].reshape((1, n_input, 1))
# for i in range(len(test)):
#     # predict the week
#     prediction_sequence = model.predict(sequence, verbose=verbose)
#     prediction_sequence = (np.around(prediction_sequence, 2)).reshape(1, 1, 1)
#     # store the predictions
#     predictions.append(prediction_sequence)
#     sequence = np.concatenate((sequence[:,1:,:], prediction_sequence), axis=1) 
#     sequence = sequence.reshape((1, n_input, 1))
# # evaluate predictions days for each week
# predictions = np.array(predictions)
# predictions = predictions.ravel()

# Calculate evaluation metrics
mae = mean_absolute_error(test, predictions)
mse = mean_squared_error(test, predictions)
rmse = np.sqrt(mse)
r2 = r2_score(test, predictions)

print("Mean Absolute Error (MAE):", mae)
print("Mean Squared Error (MSE):", mse)
print("Root Mean Squared Error (RMSE):", rmse)
print('R-squared (R2 Score): ', r2)

future = []
# sequence = test[-n_input:] # Get the last sequence hours of the training data
sequence = sequence.reshape((1, n_input, 1))  # Reshape to (1,24,1)
for i in range(len(X_fut)): # days for January
    sequence = X_fut[i, :].reshape((1, n_input, 1))
    # predict the week
    future_value = model.predict(sequence, verbose=0)
    # store the predictions
    future.append(future_value)
# evaluate predictions days for each week
future = np.array(future)
future = np.where((future < 3) & (target == 'GHI'), 0, future)
future = future.ravel()
future = np.around(future, 2)
pred_dates = pd.date_range(start='2022-01-01', end='2022-02-01', freq='H')[1:]

prediction_total = np.concatenate((predictions, future))

# Import results from RFR
with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\temperature_RFR_prediction.json", 'r') as f:
    temperature_RFR = json.load(f)

with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\GHI_RFR_prediction.json", 'r') as f:
    GHI_RFR = json.load(f)

plt.plot(test_df.index, test, label='Actual', linewidth=1)

plt.plot(test_df.index.append(pred_dates), prediction_total, label='Prediction_LSTM', linestyle='--', color='red', linewidth=1)
if target == 'GHI':
    plt.ylabel('GHI [W/m2]', fontsize=16)
else:
    plt.ylabel('Température [°C]',fontsize=16)

plt.legend(fontsize=16) 
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlim(pd.to_datetime('2021-12-01'),pd.to_datetime('2022-01-31'))
plt.show()

with open(target + '_LSTM_prediction.json', 'w') as f:
    json.dump(prediction_total.tolist(), f)