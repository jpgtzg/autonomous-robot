from lib.actions.action_interface import ActionInterface

class ActionScheduler():
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActionScheduler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.action = None
        self.scheduled_actions = set()

    def schedule_action(self, action):
        self.scheduled_actions.add(action)
        action.initialize()

    def run(self):
        actions_to_remove = []
        
        for action in self.scheduled_actions:
            action.execute()
            if action.is_finished():
                action.end(False)
                actions_to_remove.append(action)
        
        for action in actions_to_remove:
            self.scheduled_actions.remove(action)
