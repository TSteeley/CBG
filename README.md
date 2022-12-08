# CBG

Crystal Ball Gazing

The goal of this project is to take stock market data and test trading Strategies.

## Gather Data

This Function uses Alpha Vantage API to download market data to analyse.

## Models

A self made class that stores information like the market data, as well as the 'Buys' and executes strategies with input lambda functions. This is intentionally made to be very general and puts the emphasis on the user to input strategies, and technical indicators.

## Technical Indicators

Stored built in common indicators for ease of use, and/or demonstration purpose.

## Maximise

Takes a function and has functions that estimates the derivative, seconds derivative, Gradient vector, and Laplacian. This can be used for optimisation problems.

## Test Model

a full example of the function in action, as well a callable function for better integration with MATLAB.

## Maximise Py Fun

Matlab has excellent learning toolboxes and optimisation functions. Taking advantage of these tools helps to inform model parameters.

# Future

Right now I am focused on function creation and optimisation. This is only one approach and future aspirations is to use inference techniques with machine learning to predict the outcome at a given time.

Another future ambition is to integrate the algorithms found with alpha vantage to trade live.