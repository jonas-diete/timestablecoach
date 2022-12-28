class Timestable:
  def __init__(self, name, factors_learned, gold=False, silver=False, bronze=False, id=0):
    self.id = id
    self.name = name
    self.gold = gold
    self.silver = silver
    self.bronze = bronze
    # factors_learned will be filled like this
    # {1: FactorLearned(), 2: FactorLearned(), 3: FactorLearned(), ...}
    self.factors_learned = factors_learned