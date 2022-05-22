import networkx as nx
from pyvis.network import Network
from person import Person,Avatar
import requests

TOKEN = "Insert your access_token"
MAIN_FRIEND = set()
ALL_FRIEND = set()

class VkPerson(Person):
    def __init__(self, link: str):
        info = get_info(link)
        u_id = info['id']
        u_name = f"{info['first_name']} {info['last_name']}"
        u_c = True if 'deactivated' in info else info['is_closed']
        ava = Avatar("nophoto.png" if (u_c or info['photo_400_orig']=='https://vk.com/images/camera_400.png') else f"{u_id}.jpg")

        super().__init__(name = u_name,avatar=ava,id = u_id)
        self._friend_list = set() if u_c else set(get_friends_id(self.id))

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
        ('fields','photo_400_orig'),
        ('v', 5.131)
    )
    info = requests.get('https://api.vk.com/method/users.get', params=user_q).json()
    info = info['response'][0]
    p = requests.get(info['photo_400_orig'])
    out = open(f"images/{info['id']}.jpg", "wb")
    out.write(p.content)
    out.close()
    return info

def createSubVkNode(graph,person):
    ALL_FRIEND.add(person.id)
    graph.add_node(person.id,label=person.name,shape='image',  image = person.get_path())
    for friend_id in person._friend_list:
        if friend_id in ALL_FRIEND:
            graph.add_edge(person.id, friend_id)

def createMainVkNode(graph,person):
    graph.add_node(person.id, label=person.name, shape='image', image=person.get_path())
    for friend_id in person._friend_list:
        print(f"[+]  {friend_id}")
        friend_id = int(friend_id)
        MAIN_FRIEND.add(friend_id)
        createSubVkNode(graph,VkPerson(link=f"https://vk.com/id{friend_id}"))
        graph.add_edge(person.id, friend_id)

def main():
    graph = nx.Graph()
    link = input("Profile link:")
    createMainVkNode(graph,VkPerson(link=link))
    net = Network(height="100hw", width="100%")
    net.repulsion(node_distance=300)
    net.from_nx(graph)
    net.show("GFriend_FOP.html")

if __name__ == '__main__':
    main()