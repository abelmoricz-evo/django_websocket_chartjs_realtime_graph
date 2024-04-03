import math

def exp(x):
    CONSTANT = 0.01053
    return round (math.exp( CONSTANT * x - 10 ), 6 ) # six sigma

if __name__ == "__main__":

    total_liter_added = 0
    for i in range(0,100):
        total_liter_added = round( total_liter_added + exp(i), 6)
        in_acid_expected = exp(i)
        print(f"{i}     {in_acid_expected}     {total_liter_added}")