from google_drive_service import GoogleDriveService
from streamlit_google_oauth import make_signed_state, verify_signed_state


class Req:
    def __init__(self, data): self.data = data
    def execute(self): return self.data


class Files:
    def __init__(self, info): self.info = info
    def get(self, **kwargs): return Req(self.info)


class About:
    def __init__(self, user): self.user = user
    def get(self, **kwargs): return Req({"user": self.user})


class FakeService:
    def __init__(self, info, user): self._files = Files(info); self._about = About(user)
    def files(self): return self._files
    def about(self): return self._about


def identity(info):
    user = {"displayName": "Test", "emailAddress": "u@example.com", "permissionId": "p1"}
    return GoogleDriveService(FakeService(info, user)).current_identity("root")


def test_roles():
    owner = identity({"id":"root","mimeType":"application/vnd.google-apps.folder","ownedByMe":True,"capabilities":{"canEdit":True}})
    assert owner.role == "admin" and owner.drive_role == "owner"
    editor = identity({"id":"root","mimeType":"application/vnd.google-apps.folder","ownedByMe":False,"capabilities":{"canEdit":True}})
    assert editor.role == "update" and editor.drive_role == "writer"
    reader = identity({"id":"root","mimeType":"application/vnd.google-apps.folder","ownedByMe":False,"capabilities":{"canEdit":False}})
    assert reader.role == "read" and reader.drive_role == "reader"


def test_state():
    state = make_signed_state("secret")
    assert verify_signed_state(state, "secret")
    assert not verify_signed_state(state, "other")


if __name__ == "__main__":
    test_roles(); test_state(); print("OK")
