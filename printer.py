class Printer():

    async def sheet_reader(self, ctx, data):
        text = ""
        for key in data:
            if key == "_id" or key == "player":
                pass
            elif key == "name":
                text = text + f"\n-----| {data[key]} |-----\n\n"
            elif key == "strength":
                text = text + f"\n------| Skills |----- \n ---- {key} : {data[key]} ---- \n"
            elif key == "bonds":
                pass
            elif key == "inventory":
                pass
            else:
                text = text + f"---- {key} : {data[key]} ---- \n"
        await ctx.channel.send(text)

    async def bonds_reader(self, ctx, data):
        bonds = "\n ---------| Bonds |--------- \n \n"
        for b in data:
            bonds = bonds + f"-- {b} -- \n"
        
        await ctx.channel.send(bonds)

    async def inventory_reader(self, ctx, data):
        inventory = f"\n ---------| Inventory |--------- \n \n"

        for i in data["inv_list"]:
            if i["info"] == "special-item":
                inventory = inventory + "---" + i["name"] + " : "+ i["description"] + "---\n"
            elif i["info"] == "weapon":
                inventory = inventory + "---" + i["name"] + "\n + damage: "+ str(i["damage"]) + "\n"
            else:
                inventory = inventory + "---" + i["name"] + "---\n"

        await ctx.channel.send(inventory)

