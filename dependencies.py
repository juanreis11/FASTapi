from models import Usuario, db
from main import SECRET_KEY, ALGORITHM, Oauth2_schema
from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError
def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(Oauth2_schema), session: Session = Depends(pegar_sessao)):
 try:        
     dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
     id_usuario = int(dic_info.get("sub"))
 except JWTError:
     
     raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
 usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
 if not usuario:
    raise HTTPException(status_code=401, detail="Usuário invalido .")

 return usuario