import connexion

from connexion import NoContent

def get_organization(pet_id):
    return (NoContent, 405)

def update_organization(pet_id):
    return (NoContent, 405)

def delete_organization(pet_id):
    return (NoContent, 405)

def list_organizations(pet_id):
    return (NoContent, 405)

def create_organization(pet_id):
    return (NoContent, 405)

def get_document(pet_id):
    return (NoContent, 405)

def update_document(pet_id):
    return (NoContent, 405)

def delete_document(pet_id):
    return (NoContent, 405)

def list_documents(pet_id):
    return (NoContent, 405)

def create_document(pet_id):
    return (NoContent, 405)

def get_user(pet_id):
    return (NoContent, 405)

def update_user(pet_id):
    return (NoContent, 405)

def delete_user(pet_id):
    return (NoContent, 405)

def list_users(pet_id):
    return (NoContent, 405)

def create_user(pet_id):
    return (NoContent, 405)

app = connexion.App(__name__)
app.add_api('spec/swagger.yaml')
app.run(port=5000)
