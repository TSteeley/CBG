# CBG

Crystal Ball Gazing
Reshuffle

This reshuffle is a major update and will be completely distinct from the previous version in approach but the same in aim.

I have a pretty significant wishlist for this version.

## Issues with previous verison

My last version was poorly planned and ended up becoming a complicated web of functions.

The reason it became untidy is not cause I didn't plan just that I didn't really know what I was planning for. I've never made something this complex so without the experience it was kind of impossible to do it well first try.

It became a complicated web of functions because i want a lot of diversoty on strategies and approaches but I also wanted the simplicity of calling a single command to access any part. This quickly made sections large and frankly remembering how everything worked and finding errors became a nightmare.

## changes and goals

The biggest change is that what i would refer to as the internal infrastructure i.e. the parts the deal with the testing and execution of the model are completely separated from sections that manage data interpretation and manipulation. Instead data handling is done by writing a lambda function that is passed into the main function when initialising all the data. This has the advantage that issues with data manipulation are issues with the specific lambda function and the main CBG class does not have to remember all the data manipulation techniques.

My goal moving forward is to build back all of the functionality with a big increase in simplicity and readability and speed.
