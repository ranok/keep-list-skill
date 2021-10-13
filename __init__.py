from mycroft import MycroftSkill, intent_file_handler
import gkeepapi

class KeepList(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
        self.keep = None

    def initialize(self):
        '''Pulls the configuration from settings to attempt login'''
        self.retry_login()
        self.settings_change_callback = self.retry_login

    def get_list(self, query):
        if self.keep == None:
            return None
        self.keep.sync()
        lists = list(self.keep.find(query = query))
        if len(lists) == 1:
            return lists[0]
        return None

    def try_create_lists(self):
        if self.keep is None:
            return False
        if self.get_list('Mycroft Shopping List') is None:
            self.keep.createList('Mycroft Shopping List', [])
        if self.get_list('Mycroft Todo List') is None:
            self.keep.createList('Mycroft Todo List', [])

    def search_list(self, l, item):
        '''Searches for the presence of an item in the list'''
        for i in l.items:
            if item.lower() == i.text.lower():
                return (True, i.checked)
        return (False, False)

    def add_list_item(self, l, item):
        l.add(item, False)
        self.sync_keep()
    
    def sync_keep(self):
        if self.keep is not None:
            self.keep.sync()

    def uncheck_item(self, l, item):
        for i in l.items:
            if item.lower() == i.text.lower():
                i.checked = False
        self.sync_keep()

    def retry_login(self):
        '''If the settings are changed, retry to login'''
        email = self.settings.get('keep_username', '')
        password = self.settings.get('keep_password', '')
        if email is None or password is None:
            self.log.warning('Either e-mail or password is None')
            return
        try:
            self.keep = gkeepapi.Keep()
            self.keep.login(email, password)
            self.try_create_lists()
            self.log.info('Login to Google Keep successful')
        except gkeepapi.exception.LoginException:
            self.log.info('Unable to login to Google Keep')
            self.speak('Unable to log in to Google Keep')
            self.keep = None

    @intent_file_handler('shopping.list.intent')
    def handle_shopping_list(self, message):
        slist = self.get_list('Mycroft Shopping List')
        if slist is None:
            self.speak('Unable to find your shopping list')
            return
        item = message.data.get('item')
        if item is not None:
            res = self.search_list(slist, item)
            if res[0]:
                if res[1]:
                    self.uncheck_item(slist, item)
                    self.speak(item + ' was on your shopping list as done, so I unchecked it for you')
                else:
                    self.speak(item + ' is already on your shopping list')
            else:
                self.add_list_item(slist, item.capitalize())
                self.speak('Added ' + item + ' to your shopping list')
        else:
            self.speak('Sorry, I did not catch what you wanted to add, please try again')
    

    @intent_file_handler('todo.list.intent')
    def handle_todo_list(self, message):
        slist = self.get_list('Mycroft Todo List')
        if slist is None:
            self.speak('Unable to find your to do list')
            return
        item = message.data.get('item')
        if item is not None:
            res = self.search_list(slist, item)
            if res[0]:
                if res[1]:
                    self.uncheck_item(slist, item)
                    self.speak(item + ' was on your to do list as done, so I unchecked it for you')
                else:
                    self.speak(item + ' is already on your to do list')
            else:
                self.add_list_item(slist, item.capitalize())
                self.speak('Added ' + item + ' to your to do list')
        else:
            self.speak('Sorry, I did not catch what you wanted to add, please try again')    

    @intent_file_handler('query.list.intent')
    def handle_list_query(self, message):
        lname = message.data.get('lname')
        item = message.data.get('item')
        if lname is None:
            self.speak('Unable to understand which list you were referring to, please try again')
            self.log.info(str(message.data))
            return
        if lname.find('shop') != -1:
            slist = self.get_list('Mycroft Shopping List')
            lname = 'shopping'
        else:
            slist = self.get_list('Mycroft Todo List')
            lname = 'to do'
        if item is not None:
            res = self.search_list(slist, item)
            if res[0]:
                if res[1]:
                    self.speak(item + ' was found on your ' + lname + ' list, but it is marked as done')
                else:
                    self.speak('yes, ' + item + ' is on your ' + lname + ' list')
            else:
                self.speak(item + ' was not found on your ' + lname + ' list')
        else:
            self.speak('Sorry, I did not catch your query, please try again')

    def stop(self):
        pass

def create_skill():
    return KeepList()

