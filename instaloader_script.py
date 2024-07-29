import sys
from instaloader import Instaloader, Profile

def download_profile(username):
    L = Instaloader()
    profile = Profile.from_username(L.context, username)
    L.download_profile(profile, profile_pic_only=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python3 instaloader.py <username>")
    else:
        username = sys.argv[1]
        download_profile(username)
