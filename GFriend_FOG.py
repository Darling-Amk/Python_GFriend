from art import  tprint
import time
import networkx as nx
from pyvis.network import Network
from person import Person
import requests
from token_ import TOKEN

MEMBERS = set()
ALL_FRIEND = set()

class VkPerson(Person):
    def __init__(self, link: str):
        info = get_info(link)
        u_id = info['id']
        u_name = f"{info['first_name']} {info['last_name']}"
        u_c = True if 'deactivated' in info else info['is_closed']
        ava = info['photo_400_orig']
        self.city = info['city']['title'] if 'city' in info else 'NN'
        super().__init__(name = u_name,avatar=ava,id = u_id)
        self._friend_list = set() if u_c else set(get_friends_id(self.id))

class VkGroup(Person):
    def __init__(self, link: str,filter_city):
        info = get_group_info(link)
        g_id = info['id']
        g_name = info['name']
        ava = info['photo_400']
        super().__init__(name = g_name,avatar=ava,id = g_id)
        self._friend_list = get_group_ids(link,filter_city)

def get_friends_id(id):
    member_request_params = (
        ('user_id', id),
        ('access_token', TOKEN),
        ('v', 5.131)
    )
    friend_list = requests.get('https://api.vk.com/method/friends.get', params=member_request_params).json()

    friend_list = friend_list['response']['items']
    return friend_list

def get_info(link):
    link = link.replace("https://vk.com/","")
    user_q = (
        ('user_ids', link),
        ('access_token', TOKEN),
        ('lang',"0"),
        ('fields','photo_400_orig,city'),
        ('v', 5.131)
    )
    info = requests.get('https://api.vk.com/method/users.get', params=user_q).json()
    info = info['response'][0]
    return info

def get_group_info(link):
    link = link.replace("https://vk.com/", "")
    user_q = (
        ('group_id', link),
        ('access_token', TOKEN),
        ('lang', "0"),
        ('fields', 'id,name,photo_400'),
        ('v', 5.131)
    )
    info = requests.get('https://api.vk.com/method/groups.getById', params=user_q).json()
    info = info['response'][0]
    return info

def get_group_ids(link,filter_city=""):
    MEMBERS = set()
    link = link.replace("https://vk.com/", "")
    count_q = (
        ('group_id', link),
        ('access_token', TOKEN),
        ('lang', "0"),
        ('offset', "0"),
        ('count', "0"),
        ('v', 5.131)
    )
    count = requests.get('https://api.vk.com/method/groups.getMembers', params=count_q).json()
    count = count['response']['count']
    print(f'count:{count}')
    for slice in range(count//100+1):
        q = (
            ('group_id', link),
            ('access_token', TOKEN),
            ('lang', "0"),
            ('offset', f"{slice*100}"),
            ('count', f"{100}"),
            ('v', 5.131)
        )
        items = requests.get('https://api.vk.com/method/groups.getMembers', params=q).json()

        items = set(items['response']['items'])
        MEMBERS |= items
    return  MEMBERS

def createSubVkNode(graph,person,filter_city=""):
    if filter_city and (person.city != filter_city):
        print(f"[-] {person.name}, {person.city}")
        return
    ALL_FRIEND.add(person.id)
    print(f"[+] {person.name}, {person.city}")
    graph.add_node(person.id,label=person.name,shape='image',  image = person.ava)
    for friend_id in person._friend_list:
        if friend_id in ALL_FRIEND:
            graph.add_edge(person.id, friend_id)

def createMainVkNode(graph,person,filter_city=""):
    for friend_id in person._friend_list:
        friend_id = int(friend_id)
        createSubVkNode(graph,VkPerson(link=f"https://vk.com/id{friend_id}"),filter_city=filter_city)
        time.sleep(.5)

def main():
    graph = nx.Graph()
    link = input("Group link:")
    filter_city = input("City filter:")

    createMainVkNode(graph,VkGroup(link=link,filter_city=filter_city),filter_city=filter_city)
    net = Network(height="100hw", width="100%")
    net.repulsion(node_distance=300)
    net.from_nx(graph)
    net.show("GFriend_FOG.html")

if __name__ == '__main__':
    start_time = time.time()
    tprint('GFriend_FOG',chr_ignore=True)
    main()
    print("--- %s seconds ---" % (time.time() - start_time))