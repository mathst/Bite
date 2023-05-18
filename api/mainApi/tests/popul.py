
# Criar um objeto Cardapio
from api.mainApi.models import Cardapio


cardapio = Cardapio(id_cardapio="1card1", nome="Cardápio do Restaurante", descricao="Nosso cardápio variado.")

# Adicionar alguns itens ao cardápio
item1 = {
    "id": "item1",
    "nome": "Hambúrguer",
    "descricao": "Delicioso hambúrguer caseiro",
    "ingredientes": ["Pão", "Carne", "Queijo", "Alface", "Tomate"],
}
item2 = {
    "id": "item2",
    "nome": "Pizza",
    "descricao": "Pizza de mussarela com tomate e manjericão",
    "ingredientes": ["Massa de pizza", "Molho de tomate", "Queijo mussarela", "Tomate", "Manjericão"],
}
cardapio.add_item(item1)
cardapio.add_item(item2)

# Adicionar alguns combos ao cardápio
combo1 = {
    "id": "combo1",
    "nome": "Combo Hambúrguer",
    "descricao": "Hambúrguer + Batata frita + Refrigerante",
    "itens": [
        {
            "item_id": "item1",
            "quantidade": 1,
        },
        {
            "item_id": "item2",
            "quantidade": 1,
        },
        {
            "item_id": "item3",
            "quantidade": 1,
        },
    ],
}
# Adicionar mais itens ao cardápio
item3 = {
    "id": "item3",
    "nome": "Salada Caesar",
    "descricao": "Salada com alface, frango grelhado, croutons e molho caesar",
    "ingredientes": ["Alface", "Frango grelhado", "Croutons", "Molho Caesar"],
}
item4 = {
    "id": "item4",
    "nome": "Sushi",
    "descricao": "Sushi de salmão com arroz e nori",
    "ingredientes": ["Salmão", "Arroz", "Nori"],
}
cardapio.add_item(item3)
cardapio.add_item(item4)

# Adicionar mais combos ao cardápio
combo2 = {
    "id": "combo2",
    "nome": "Combo Pizza",
    "descricao": "Pizza + Refrigerante",
    "itens": [
        {
            "item_id": "item2",
            "quantidade": 1,
        },
        {
            "item_id": "item3",
            "quantidade": 1,
        },
        {
            "item_id": "item4",
            "quantidade": 1,
        },
    ],
}
combo3 = {
    "id": "combo3",
    "nome": "Combo Sushi",
    "descricao": "Sushi + Chá verde",
    "itens": [
        {
            "item_id": "item4",
            "quantidade": 2,
        },
        {
            "item_id": "item5",
            "quantidade": 1,
        },
    ],
}
cardapio.add_combo(combo1)
cardapio.add_combo(combo2)
cardapio.add_combo(combo3)

# Listar os itens e combos do cardápio
itens_cardapio, combos_cardapio = cardapio.listar_itens_cardapio()
print("Itens do cardápio:")
for item in itens_cardapio:
    print(item)

print("Combos do cardápio:")
for combo in combos_cardapio:
    print(combo)
