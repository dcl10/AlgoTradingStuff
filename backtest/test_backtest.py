import unittest
from backtest.backtest import BackTester


class TestBackTester(unittest.TestCase):

    def test_selling(self):
        instructions = [0, 0, 0]
        prices = [1, 1, 1]
        answer = 100.00
        margin = 0.01
        for i, p in zip(instructions, prices):
            answer += (answer * margin) * p
        bt = BackTester(100.00, instructions, prices, margin)
        bt.run()
        self.assertEqual(answer, bt.result)

    def test_buying(self):
        instructions = [1, 1, 1]
        prices = [1, 1, 1]
        answer = 100.00
        margin = 0.01
        for i, p in zip(instructions, prices):
            answer -= (answer * margin) * p
        bt = BackTester(100.00, instructions, prices, margin)
        bt.run()
        self.assertEqual(answer, bt.result)


if __name__ == '__main__':
    unittest.main()
