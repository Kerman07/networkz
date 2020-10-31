from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.TextField()
    time_posted = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    user = models.ForeignKey("User", on_delete=models.CASCADE,
                             related_name="posts")

    def user_like(self, user):
        return True if self.liked_by.filter(likes=user) else False
    
    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user.id,
            "username": self.user.username,
            "time_posted": self.time_posted.strftime("%b. %d, %Y, %I:%M %p"),
            "likes": self.likes
        }
    
class UserFollowing(models.Model):
    user_id = models.ForeignKey("User", on_delete=models.CASCADE,
                                related_name="following")
    following_user_id = models.ForeignKey("User", on_delete=models.CASCADE,
                                           related_name="followers")

class Like(models.Model):
    liked_by = models.ForeignKey("Post", on_delete=models.CASCADE,
                                 related_name="liked_by")
    likes = models.ForeignKey("User", on_delete=models.CASCADE,
                              related_name="likes")