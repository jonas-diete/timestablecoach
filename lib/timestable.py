class Timestable:
  def __init__(self, name, factors_learned):
    self.id = 0
    self.name = name
    self.gold = False
    self.silver = False
    self.bronze = False
    # factors_learned will be filled like this
    # {1: FactorLearned(), 2: FactorLearned(), 3: FactorLearned(), ...}
    self.factors_learned = factors_learned