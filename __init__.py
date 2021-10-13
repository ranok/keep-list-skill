from mycroft import MycroftSkill, intent_file_handler
import gkeepapi

class KeepList(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('list.keep.intent')
    def handle_list_keep(self, message):
        self.speak_dialog('list.keep')


def create_skill():
    return KeepList()

