from asyncio import sleep
from fortnitepy.ext import commands
from fortnitepy import ReadyState, Friend, Optional
from FortniteAPIAsync import APIClient
from lib import Color


class PartyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.dm_only()
    @commands.command(
        name="leave",
        description="Quitter la partie",
    )
    async def leave(self, ctx: commands.Context) -> None:
        await self.bot.party.me.set_emote('EID_Wave')
        await sleep(2)
        await self.bot.party.me.leave()

    @commands.dm_only()
    @commands.command(
        name="lead",
        description="Promouvoir un membre du groupe en chef",
    )
    async def lead(self, ctx: commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.bot.fetch_user(ctx.author.display_name)
        else:
            user = await self.bot.fetch_user(epic_username)

            if user is None:
                await ctx.send(f"Je ne trouve pas {epic_username}")
                return

        member = self.bot.party.get_member(user.id)
        try:
            await member.promote()
            await ctx.send(f"{member.display_name} a été promu chef du groupe")
        except:
            await ctx.send("Je ne suis pas chef du groupe")

    @commands.dm_only()
    @commands.command(
        name="kick",
        description="Expulser un membre du groupe",
    )
    async def kick(self, ctx: commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.bot.fetch_user(ctx.author.display_name)
        else:
            user = await self.bot.fetch_user(epic_username)

            if user is None:
                await ctx.send(f"Je ne trouve pas {epic_username}")
                return

        member = self.bot.party.get_member(user.id)
        try:
            await member.kick()
            await ctx.send(f"{member.display_name} a été expulsé du groupe")
        except:
            await ctx.send("Je ne suis pas chef du groupe")

    @commands.dm_only()
    @commands.command(
        name="invite",
        description="Inviter un membre dans le groupe",
    )
    async def _invite(self, ctx: commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            epic_friend = self.bot.get_friend(ctx.author.id)
        else:
            user = await self.bot.fetch_user(epic_username)

            if user is not None:
                epic_friend = self.bot.get_friend(user.id)
            else:
                epic_friend = None
                await ctx.send(f"Je ne trouve pas {epic_username}")

        if isinstance(epic_friend, Friend):
            try:
                await epic_friend.invite()
                await ctx.send(f"Invitation envoyée à {epic_friend.display_name}")
            except:
                await ctx.send(f"Impossible d'inviter {epic_friend.display_name} dans le groupe")
        else:
            await ctx.send("Je ne trouve pas ce joueur")

    @commands.dm_only()
    @commands.command(
        name="ask",
        description="Demander à rejoindre le groupe",
    )
    async def ask(self, ctx: commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            epic_friend = self.bot.get_friend(ctx.author.id)
        else:
            user = await self.bot.fetch_user(epic_username)

            if user is not None:
                epic_friend = self.bot.get_friend(user.id)
            else:
                epic_friend = None
                await ctx.send(f"Je ne trouve pas {epic_username}")

        if isinstance(epic_friend, Friend):
            try:
                await epic_friend.request_to_join()
                await ctx.send(f"Demande envoyée à {epic_friend.display_name}")
            except:
                await ctx.send(f"Impossible d'envoyer une demande à {epic_friend.display_name}")
        else:
            await ctx.send("Je ne trouve pas ce joueur")

    @commands.dm_only()
    @commands.command(
        name="join",
        description="Rejoindre un ami",
    )
    async def join(self, ctx: commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            epic_friend = self.bot.get_friend(ctx.author.id)
        else:
            user = await self.bot.fetch_user(epic_username)

            if user is not None:
                epic_friend = self.bot.get_friend(user.id)
            else:
                epic_friend = None
                await ctx.send(f"Je ne trouve pas {epic_username}")

        if isinstance(epic_friend, Friend):
            try:
                await epic_friend.join_party()
                await ctx.send(f"Rejoins {epic_friend.display_name}")
            except:
                await ctx.send(f"Impossible de rejoindre {epic_friend.display_name}")
        else:
            await ctx.send("Je ne trouve pas ce joueur")

    @commands.dm_only()
    @commands.command(
        name="inviteall",
        description="Ajouter tous les amis du bot dans le groupe",
    )
    async def inviteall(self, ctx: commands.Context) -> None:
        success = []
        failed = []
        for friend in self.bot.friends:
            try:
                await friend.invite()
                success.append(friend.display_name)
            except:
                failed.append(friend.display_name)
        await ctx.send(f"Invitations envoyées ({len(success)}): {', '.join(success)}")
        if failed:
            await ctx.send(f"Invitations non envoyées ({len(failed)}): {', '.join(failed)}")

    @commands.dm_only()
    @commands.command(
        name="askall",
        description="Demander à rejoindre le groupe à tous les amis du bot",
    )
    async def askall(self, ctx: commands.Context) -> None:
        success = []
        failed = []
        for friend in self.bot.friends:
            try:
                await friend.request_to_join()
                success.append(friend.display_name)
            except:
                failed.append(friend.display_name)
        await ctx.send(f"Demandes envoyées ({len(success)}): {', '.join(success)}")
        if failed:
            await ctx.send(f"Demandes non envoyées ({len(failed)}): {', '.join(failed)}")

    @commands.dm_only()
    @commands.command(
        name="addall",
        description="Ajouter tous les membres du groupe en amis",
    )
    async def addall(self, ctx: commands.Context) -> None:
        success = []
        failed = []
        for member in self.bot.party.members:
            try:
                await member.add()
                success.append(member.display_name)
            except:
                failed.append(member.display_name)
        await ctx.send(f"Amis ajoutés ({len(success)}): {', '.join(success)}")
        if failed:
            await ctx.send(f"Amis non ajoutés ({len(failed)}): {', '.join(failed)}")

    @commands.dm_only()
    @commands.command(
        name="deleteall",
        description="Supprimer tous les membres du groupe en amis",
    )
    async def deleteall(self, ctx: commands.Context) -> None:
        success = []
        failed = []
        for member in self.bot.party.members:
            if member.id == ctx.author.id:
                continue
            try:
                await member.delete()
                success.append(member.display_name)
            except:
                failed.append(member.display_name)
        await ctx.send(f"Amis supprimés ({len(success)}): {', '.join(success)}")
        if failed:
            await ctx.send(f"Amis non supprimés ({len(failed)}): {', '.join(failed)}")

    @commands.dm_only()
    @commands.command(
        name="blockall",
        description="Supprimer tous les membres du groupe en amis",
    )
    async def blockall(self, ctx: commands.Context) -> None:
        success = []
        failed = []
        for member in self.bot.party.members:
            if member.id == ctx.author.id:
                continue
            try:
                await member.block()
                success.append(member.display_name)
            except:
                failed.append(member.display_name)
        await ctx.send(f"Personnes bloquées ({len(success)}): {', '.join(success)}")
        if failed:
            await ctx.send(f"Personnes non bloquées ({len(failed)}): {', '.join(failed)}")

    @commands.dm_only()
    @commands.command(
        name="ready",
        description="Prêt à jouer",
    )
    async def ready(self, ctx: commands.Context) -> None:
        await self.bot.party.me.set_ready(ReadyState.READY)
        await ctx.send("Prêt à jouer")

    @commands.dm_only()
    @commands.command(
        name="unready",
        description="Ne pas être prêt à jouer",
    )
    async def unready(self, ctx: commands.Context) -> None:
        await self.bot.party.me.set_ready(ReadyState.NOT_READY)
        await ctx.send("Ne pas être prêt à jouer")

    @commands.dm_only()
    @commands.command(
        name="sitout",
        description="Ne pas jouer",
    )
    async def sitout(self, ctx: commands.Context) -> None:
        await self.bot.party.me.set_ready(ReadyState.SITTING_OUT)
        await ctx.send("Ne pas jouer")


class CosmeticCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.fortnite_api = APIClient()

    @commands.dm_only()
    @commands.command(
        name="skin",
        description="Changer de skin",
    )
    async def skin(self, ctx: commands.Context, *, skin: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=skin,
                backendType="AthenaCharacter",
            )

            await self.bot.party.me.set_outfit(cosmetic.id)
            await ctx.send(f"Skin changé en {cosmetic.name}")
        except:
            await ctx.send("Skin introuvable")

    @commands.dm_only()
    @commands.command(
        name="pickaxe",
        description="Changer de pioche",
    )
    async def pickaxe(self, ctx: commands.Context, *, pickaxe: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=pickaxe,
                backendType="AthenaPickaxe",
            )

            await self.bot.party.me.set_pickaxe(cosmetic.id)
            await ctx.send(f"Pioche changée en {cosmetic.name}")
        except:
            await ctx.send("Pioche introuvable")

    @commands.dm_only()
    @commands.command(
        name="backpack",
        description="Changer de sac à dos",
    )
    async def backpack(self, ctx: commands.Context, *, backpack: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=backpack,
                backendType="AthenaBackpack",
            )

            await self.bot.party.me.set_backpack(cosmetic.id)
            await ctx.send(f"Sac à dos changé en {cosmetic.name}")
        except:
            await ctx.send("Sac à dos introuvable")

    @commands.dm_only()
    @commands.command(
        name="emote",
        description="Changer d'emote",
    )
    async def emote(self, ctx: commands.Context, *, emote: Optional[str] = None) -> None:
        if emote is None:
            await self.bot.party.me.clear_emote()
            await ctx.send("Emote retirée")
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                    lang="fr",
                    searchLang="fr",
                    matchMethod="contains",
                    name=emote,
                    backendType="AthenaDance",
                )

                await self.bot.party.me.set_emote(cosmetic.id)
                await ctx.send(f"Emote changée en {cosmetic.name}")
            except:
                await ctx.send("Emote introuvable")

    @commands.dm_only()
    @commands.command(
        name="pet",
        description="Changer d'animal de compagnie",
    )
    async def pet(self, ctx: commands.Context, *, pet: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=pet,
                backendType="AthenaPet",
            )

            await self.bot.party.me.set_pet(cosmetic.id)
            await ctx.send(f"Animal de compagnie changé en {cosmetic.name}")
        except:
            await ctx.send("Animal de compagnie introuvable")

    @commands.dm_only()
    @commands.command(
        name="emoji",
        description="Changer d'emoji",
    )
    async def emoji(self, ctx: commands.Context, *, emoji: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=emoji,
                backendType="AthenaEmoji",
            )

            await self.bot.party.me.set_emoji(cosmetic.id)
            await ctx.send(f"Emoji changé en {cosmetic.name}")
        except:
            await ctx.send("Emoji introuvable")

    @commands.dm_only()
    @commands.command(
        name="contrail",
        description="Changer de trainée",
    )
    async def contrail(self, ctx: commands.Context, *, contrail: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(
                lang="fr",
                searchLang="fr",
                matchMethod="contains",
                name=contrail,
                backendType="AthenaContrail",
            )

            await self.bot.party.me.set_contrail(cosmetic.id)
            await ctx.send(f"Trainée changée en {cosmetic.name}")
        except:
            await ctx.send("Trainée introuvable")

    @commands.dm_only()
    @commands.command(
        name="hologram",
        description="Mettre un hologramme",
    )
    async def hologram(self, ctx: commands.Context) -> None:
        await self.bot.party.me.set_outfit("CID_VIP_Athena_Commando_M_GalileoGondola_SG")

        await ctx.send("Skin changé en hologramme")


class MiscCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.dm_only()
    @commands.command(
        name="bp",
        description="Définir le niveau du battle pass",
    )
    async def bp(self, ctx: commands.Context, level: int) -> None:
        await self.bot.party.me.set_battlepass_info(has_purchased=True, level=level)
        await ctx.send(f"Battle pass mis au niveau {level}")

    @commands.dm_only()
    @commands.command(
        name="level",
        description="Définir le niveau du compte",
    )
    async def level(self, ctx: commands.Context, level: int) -> None:
        await self.bot.party.me.set_banner(season_level=level)
        await ctx.send(f"Niveau du compte mis au niveau {level}")

    @commands.dm_only()
    @commands.command(
        name="findparty",
        aliases=["party", "partie", "game", "jeu"],
        description="Trouver une partie",
    )
    async def findparty(self, ctx: commands.Context, *, join: Optional[str] = "on") -> None:
        partylist = {}
        cached = []
        message = "Parties disponibles :\n"
        await ctx.send("Recherche de parties...")
        for friend in self.bot.friends:
            try:
                party = await friend.join_party()
                if party.id in cached:
                    continue
                cached.append(party.id)
                partylist[friend.display_name] = party.member_count - 1
            except:
                pass

        await self.bot.party.me.leave()
        cleanlist = dict(sorted(partylist.items(), key=lambda item: item[1], reverse=True))

        for key, value in cleanlist.items():
            message += f"{key}: {value} membres\n"
        
        await ctx.send(message)

        keylist = [str(key) for key in cleanlist.keys()]

        if join != "off":
            user = await self.bot.fetch_user(keylist[0])
            friend = self.bot.get_friend(user.id)

            try:
                await friend.join_party()
                await self.bot.party.invite(ctx.author.id)
            except:
                await ctx.send("Impossible de rejoindre la partie")
    
    @commands.dm_only()
    @commands.command(
        name="friendlist",
        aliases=["friends"],
        description="Afficher la liste d'amis",
    )
    async def friendlist(self, ctx: commands.Context) -> None:
        message = f"Liste d'amis ({len([value for value in self.bot.friends if value.is_online])}):\n"
        console_message = "Liste d'amis: "
        for friend in self.bot.friends:
            if friend.is_online:
                message += f"{friend.display_name} ({friend.platform or '?'})\n"
                console_message += f"{friend.display_name}, "
        
        await ctx.send(message)
        print(console_message)

    @commands.dm_only()
    @commands.command(
        name="addallmode",
        description="Défini si le bot doit ajouter tous les membres du groupe en amis",
    )
    async def addallmode(self, ctx: commands.Context, *, mode: str) -> None:
        if mode == "on":
            self.bot.add_all_mode = True
            for member in self.bot.party.members:
                try:
                    await member.add()
                    await ctx.send(f"Ajouté {member.display_name} en ami")
                except:
                    pass
            await ctx.send("Le bot va ajouter tous les membres du groupe en amis")
        elif mode == "off":
            self.bot.add_all_mode = False
            await ctx.send("Le bot ne va pas ajouter tous les membres du groupe en amis")
        else:
            await ctx.send("Mode invalide")

    @commands.dm_only()
    @commands.command(
        name="resmode",
        description="Défini si le bot doit découvrir et ajouter tous les membres des groupes en amis",
    )
    async def resmode(self, ctx: commands.Context, *, mode: str, time: Optional[int] = 0) -> None:
        await sleep(time)
        if mode == "on":
            self.bot.research_mode = True
            await ctx.send("Le bot va découvrir et ajouter tous les membres des groupes en amis")

            while self.bot.research_mode:
                print(f"{Color.MAGENTA}[RESMODE] {Color.LIGHT_MAGENTA}Recherche de groupes en cours...")
                added = []
                cached = []
                for friend in self.bot.friends:
                    try:
                        party = await friend.join_party()
                        if party.id in cached:
                            continue
                        for member in party.members:
                            try:
                                await member.add()
                                added.append(member.display_name)
                                cached.append(party.id)
                            except:
                                pass
                    except:
                        pass
                await self.bot.party.me.leave()
                print(f"{Color.MAGENTA}[RESMODE] {Color.LIGHT_MAGENTA}Recherche de groupes terminée.\nAmis ajoutés ({len(added)}): {', '.join(added)}")
                await sleep(600)
        elif mode == "off":
            self.bot.research_mode = False
            await ctx.send("Le bot ne va plus découvrir et ajouter tous les membres des groupes en amis")
        elif mode == "status":
            if self.bot.research_mode:
                await ctx.send("Le bot est en mode recherche")
            else:
                await ctx.send("Le bot n'est pas en mode recherche")
        elif mode == "now":
            print(f"{Color.MAGENTA}[RESMODE] {Color.LIGHT_MAGENTA}Recherche de groupes en cours...")
            added = []
            cached = []
            for friend in self.bot.friends:
                try:
                    party = await friend.join_party()
                    if party.id in cached:
                        continue
                    for member in party.members:
                        try:
                            await member.add()
                            added.append(member.display_name)
                            cached.append(party.id)
                        except:
                            pass
                except:
                    pass
            await self.bot.party.me.leave()
            await ctx.send(f"Recherche de groupes terminée.\nAmis ajoutés ({len(added)}): {', '.join(added)})")
        else:
            await ctx.send("Mode invalide")
    
    @commands.dm_only()
    @commands.command(
        name="block",
        description="Bloquer un joueur",
    )
    async def block(self, ctx: commands.Context, *, user: str) -> None:
        user = await self.bot.fetch_user(user)
        friend = self.bot.get_friend(user.id)

        try:
            await friend.block()
            await ctx.send(f"{friend.display_name} a été bloqué")
        except:
            await ctx.send("Impossible de bloquer le joueur")
    
    @commands.dm_only()
    @commands.command(
        name="unblock",
        description="Débloquer un joueur",
    )
    async def unblock(self, ctx: commands.Context, *, user: str) -> None:
        user = await self.bot.fetch_user(user)
        friend = self.bot.get_friend(user.id)

        try:
            await friend.unblock()
            await ctx.send(f"{friend.display_name} a été débloqué")
        except:
            await ctx.send("Impossible de débloquer le joueur")
    
    @commands.dm_only()
    @commands.command(
        name="add",
        description="Ajouter un joueur en ami",
    )
    async def add(self, ctx: commands.Context, *, user: str) -> None:
        user = await self.bot.fetch_user(user)
        friend = self.bot.get_friend(user.id)

        try:
            await friend.add()
            await ctx.send(f"{friend.display_name} a été ajouté en ami")
        except:
            await ctx.send("Impossible d'ajouter le joueur en ami")

    @commands.dm_only()
    @commands.command(
        name="remove",
        description="Retirer un joueur de la liste d'amis",
    )
    async def remove(self, ctx: commands.Context, *, user: str) -> None:
        user = await self.bot.fetch_user(user)
        friend = self.bot.get_friend(user.id)

        try:
            await friend.remove()
            await ctx.send(f"{friend.display_name} a été retiré de la liste d'amis")
        except:
            await ctx.send("Impossible de retirer le joueur de la liste d'amis")
