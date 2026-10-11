from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema
from models import ItemPedido, Pedido, Usuario

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/lista")
async def pedidos():
    """
    Esta rota é responsável por listar os pedidos. Todas as rotas dos pedidos precisam de autenticação
    """
    return {"message": "Você acessou a  rota de pedidos!"}

@order_router.post("/pedido")

async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """
    Esta rota é responsável por criar um novo pedido.
    """
    novo_pedido = Pedido(usuario=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}!"}
@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para fazer essa modificação.")
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"Pedido número {id_pedido} cancelado com sucesso!",
        "pedido": pedido
            }
@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if usuario.admin == False:
        raise HTTPException(status_code=401, detail="Você não tem permissão para acessar essa rota.")
    else:
        pedidos = session.query(Pedido).all()
        return{
            "pedidos": pedidos
        }
@order_router.post("/pedido/adicionar_item/{id_pedido}")
async def adicionar_item(id_pedido: int,item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem permissão para fazer essa modificação.")
    item_pedido = ItemPedido(quantidade=item_pedido_schema.quantidade, sabor=item_pedido_schema.sabor, tamanho=item_pedido_schema.tamanho, preco_unitario=item_pedido_schema.preco_unitario, pedido=id_pedido)
    pedido.calcular_preco()
    session.add(item_pedido)
    session.commit()
    return {
        "mensagem": f"Item adicionado ao pedido número {id_pedido} com sucesso!",
        "preco_pedido": pedido.preco
            }