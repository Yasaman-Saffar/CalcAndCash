class GroupErrors(Exception):
    pass

class HasGroup(GroupErrors):
    pass

class HasInvited(GroupErrors):
    pass


class GroupQuestionErrors(Exception):
    pass

class NotAnswered(GroupQuestionErrors):
    pass

class WrongAnswered(GroupQuestionErrors):
    pass