# CBG

Crystal Ball Gazing
Reshuffle

This reshuffle is a major update and will be completely distinct from the previous version in approach but the same in aim.

I have a pretty significant wishlist for this version.

## Goals

### Create a proper main file

A lot of my setup is done in jupyter notebooks and the main is in a file not called main. A large part of restructuring all of this will be done with introducing a proper main file. GUI is a big maybe I have a lot I want to do first.

### Make my code more robust and error handling easier

Right now going through making fixes everything feels very out of hand and everything has a follow on efect I need to consider. I believe a better implementation
of OOP will help me achieve this.

### integrate new services

keeping track of all of the models I have run locally is cool but I want to be able to run code from virtual machines for better power and in the future I want to allow others to work with my project. In its current form this wopuld be impossible so I want to create a database hosted by a cloud service that my code can interact with, be given a model to run, run the model, and then return the best answer it finds. The most major part of this update is orienting the project in this direction.

### Create a live version

It's all good and well to create strategies but it's useless if you never use them. the live version has been a long time coming and represents many new challenges.

## Backtesting

### Gather Data

Gather data and the data it collects are being completely changed. Previously data would be downloaded from AlphaVantage at one minute time step interpreted into 1 hour time step with some indicators created along the way, and finally more indactors added in the one hour time step. this is great but it leads to large files. For 10 positions, the raw and interpretted data took up 104 Mb of data since it consisted of owver 3 million lines of data.

I believe theres no reason the raw data cant be interpretted on demand and further only create the indicators that will be used to be more ram friendly. 100Mb probably isn't massive but it seems like a scaling issue waiting to happen.

### Models

Models is the super class of ihttt and weighted indicators.

I'm invisaging this part as the house that everything lives in. In the future I can see gather data becoming a method inside of models. This will be a constantly running object and assessing new models will be a case of changing some variables.

### ihttt & weighted indicators

These will subclass from Models. these two will implement different rule sets. likely these will have weights that need to be adjusted to optimise the outcome.

My main goal is to make these very simple to implement new strategies. IHTTT should focus on algorithms like 'crossover' or other rules bvased approaches and quickly being able to write and implement the logic for these without needing to edit source code and still being able to optimise some varibles I think are very important features.

### optimise output

#### Use better learning

this is one of opr the most important oart of this poroject... and right now it's bad.

Right now I am using SCIPY minimsie to optimise my models. frankly its the first thing that worked. I am very sure this is super inefficient. Each model from the last version takes hours to analyse and the results are shit, right now I feel like the only upside is that it works. I am going to implement tensor flow and unless it's not significantly better which I expect it will be I will probably just remove SCIPY minimise from this project and probably just my memory too.

#### My Goals and Issues

This will be a method in the Models Object. as it stands this wound up become basically my main since I implemented Multiple Processing, but I think it's a symptom manifested by me not planning things out perfectly.

The planning side of things I find the most difficult because I'm learning on the go and preplanning for multiple processing when you've never heard of it is difficult.

## Live version

Like creating a GUI it is definitely a goal but I hhave a lot I want to do first. my biggest issue is that I feel like I need to solve every other problem first before I create a whole raft of new ones.

I have been Investigating creating a rust library to speed up the backtesting and learned about TAURI. Again LOTS of issues to sort out first become I give myself many MANY new ones. But. this seems like a good way to hit Live version and GUI in one go. I will however make this version perfect first.
