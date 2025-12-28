
# You must import this helper!

from operator import itemgetter 

# Data: (Name, Access_Level, Status)


access_list = [
    ('Alpha', 5, 'Active'),
    ('Beta', 1, 'Standby'),
    ('Gamma', 5, 'Locked')
]
access_list.sort(key=itemgetter(1))
print(access_list)

