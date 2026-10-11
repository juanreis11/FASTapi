from fastapi import APIRouter, Depends, HTTPException
from models import Usuario,ItemPedido, Pedido
from sqlalchemy.orm import sessionmaker
from dependencies import pegar_sessao, verificar_token
from main import ACCESS_TOKEN_EXPIRE_MINUTES, bcrypt_context, ALGORITHM, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from security import bcrypt_context
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    encoded_jwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM) 
   
    return encoded_jwt



def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario
@auth_router.post("/")
async def home():
    """
    Esta rota é responsável por autenticar o usuário.
    """
    return {"message": "Você acessou a rota de autenticação!", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session=Depends(pegar_sessao)):    
    """
    Esta rota é responsável por criar uma nova conta de usuário.
    """
    

    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(nome=usuario_schema.nome, email=usuario_schema.email, senha=senha_criptografada, ativo=usuario_schema.ativo, admin=usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": f"usuario cadastrado com sucesso! {usuario_schema.email}"}
    

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    """
    Esta rota é responsável por autenticar o usuário.
    """
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        access_token = criar_token(usuario.id)
    return{"access_token": access_token,           
           "token_type": "Bearer"}

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
        
    }
    
    
    
    


   