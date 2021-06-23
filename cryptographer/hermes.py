'''

1. setup queue for taking in new trades
2. execute first order
3. initiate cycle for all future orders

    a. IF prediction is same direction, do same order
        - track total of all "same orders" in a row
    b. ELSE prediction is stagnant or opposite, do inverse order
        - inverse order should be same-order total from (a)

- should we hodl when it drops? sell on the way down?
- change amount based on confidence level (including inverse maybe?)
- Include regular check for failed orders

'''

class Hermes: 

    def __init__(self) -> None:
        pass