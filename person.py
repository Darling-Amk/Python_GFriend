from PIL import Image
import os

class Avatar:
    SIZE_CROP = 400
    AVATAR_STORAGE = os.path.abspath('images') + "\\avatars\\"

    @classmethod
    def cut(cls, path:str):
        image = Image.open(path)
        min_size = min(image.size)
        img_width, img_height = image.size
        im_crop = image.crop(((img_width - min_size) // 2,(img_height - min_size) // 2,
                           (img_width + min_size) // 2,(img_height + min_size) // 2))
        im_crop = im_crop.resize((cls.SIZE_CROP, cls.SIZE_CROP), Image.ANTIALIAS)
        return  im_crop

    @classmethod
    def avatar_save(cls, img:Image,name:str):
        path = cls.AVATAR_STORAGE + name
        img.save(path , quality=95)
        return path

    def __init__(self,name:str):
        img = Avatar.cut(os.path.abspath('images') +"\\"+ name)
        self.img_path = Avatar.avatar_save(img,name)

class Person:
    def __init__(self,name:str,avatar:Avatar,id:int=None):
        self.name = name
        self.ava = avatar
        self._friend_list = set()
        if id:
            self.id =id
        else:
            self.id = Person.get_id()

    PERSON_COUNT = 0
    @staticmethod
    def make_friends(self, other):
        self._add_friend(other)
        other._add_friend(self)

    @classmethod
    def get_id(cls):
        cls.PERSON_COUNT+=1
        return cls.PERSON_COUNT-1

    def _add_friend(self,friend):
        self._friend_list.add(friend)

    def get_path(self):
        return self.ava.img_path

    def __str__(self):
        s =  f"""
                name: {self.name}
                id:{self.id}
                avatar: {self.ava.img_path}
                =================
                friends:
                """
        for person in self._friend_list:
            s = s+f"{person.name}\n"
        return s
