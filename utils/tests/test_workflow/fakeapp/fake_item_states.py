from workflow.classes import State

#
# The FakeItem state machine and state implementation
#
 
def FAStateConstructor(name = None):
    if name is None: return StateCreated() # This is the first state when the model is 
                                           # created
    elif name == StateCreated.__str__(): return StateCreated()
    elif name == StateEmailed.__str__(): return StateEmailed()
    elif name == StateConsulted.__str__(): return StateConsulted()
    elif name == StateProvided.__str__(): return StateProvided()
   
class StateCreated(State):
    def go_next(self, fake_item, who):
        fake_item.context.setState(StateEmailed(), who)
    @staticmethod
    def __str__():
        return "CREATED"
 
class StateEmailed(State):
    def go_next(self, fake_item, who):
        fake_item.context.setState(StateConsulted(), who)
    @staticmethod
    def __str__():
        return "EMAILED"
       
class StateConsulted(State):
    def go_next(self, fake_item, who):
        fake_item.context.setState(StateProvided(), who)
    @staticmethod
    def __str__():
        return "CONSULTED"

class StateProvided(State):
    def go_next(self, fake_item, who):
        pass
    @staticmethod
    def __str__():
        return "PROVIDED"
