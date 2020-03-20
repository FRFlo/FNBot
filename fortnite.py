# -*- coding: utf-8 -*-

"""
“Commons Clause” License Condition v1.0
Copyright Oli 2019

The Software is provided to you by the Licensor under the
License, as defined below, subject to the following condition.

Without limiting other conditions in the License, the grant
of rights under the License will not include, and the License
does not grant to you, the right to Sell the Software.

For purposes of the foregoing, “Sell” means practicing any or
all of the rights granted to you under the License to provide
to third parties, for a fee or other consideration (including
without limitation fees for hosting or consulting/ support
services related to the Software), a product or service whose
value derives, entirely or substantially, from the functionality
of the Software. Any license notice or attribution required by
the License must also include this Commons Clause License
Condition notice.

Software: PartyBot

License: Apache 2.0
"""

try:
    # Standard library imports
    import asyncio
    import aiohttp
    import datetime
    import json
    import logging
    import sys
    import functools
    import os
    from typing import Tuple

    # Related third party imports
    import crayons
    import fortnitepy
    import fortnitepy.errors
    import BenBotAsync

except ModuleNotFoundError as e:
    print(e)
    print('Failed to import 1 or more modules, running "INSTALL PACKAGES.bat"'
          'might fix the issue, if not please create an issue or join'
          'the support server.')
    exit()

# Imports uvloop and uses it if installed (Unix only).
try:
    import uvloop 
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def time() -> str:
    return datetime.datetime.now().strftime('%H:%M:%S')


def get_device_auth_details() -> dict:
    if os.path.isfile('device_auths.json'):
        with open('device_auths.json', 'r') as fp:
            return json.load(fp)
    return {}


def store_device_auth_details(email: str, details: dict) -> None:
    existing = get_device_auth_details()
    existing[email] = details

    with open('device_auths.json', 'w') as fp:
        json.dump(existing, fp, sort_keys=False, indent=4)


async def set_vtid(vtid: str) -> Tuple[str, str, int]:
    async with aiohttp.ClientSession() as session:
        request = await session.request(
            method='GET',
            url='http://benbotfn.tk:8080/api/assetProperties',
            params={
                'file': 'FortniteGame/Content/Athena/'
                        f'Items/CosmeticVariantTokens/{vtid}.uasset'
            })

        response = await request.json()

    file_location = response['export_properties'][0]

    skin_cid = file_location['cosmetic_item']
    variant_channel_tag = file_location['VariantChanelTag']['TagName']
    variant_name_tag = file_location['VariantNameTag']['TagName']

    variant_type = variant_channel_tag.split(
        'Cosmetics.Variant.Channel.'
    )[1].split('.')[0]

    variant_int = int("".join(filter(
        lambda x: x.isnumeric(), variant_name_tag
    )))

    if variant_type == 'ClothingColor':
        return skin_cid, 'clothing_color', variant_int
    else:
        return skin_cid, variant_type, variant_int


print(crayons.cyan(f'[PartyBot] [{time()}] Bot Fortnite de FR Flo. '))

with open('config.json') as f:
    data = json.load(f)

if data['debug']:
    logger = logging.getLogger('fortnitepy.http')
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('\u001b[36m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
    logger.addHandler(handler)

    logger = logging.getLogger('fortnitepy.xmpp')
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('\u001b[35m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
    logger.addHandler(handler)

device_auth_details = get_device_auth_details().get(data['email'], {})
client = fortnitepy.Client(
    auth=fortnitepy.AdvancedAuth(
        email=data['email'],
        password=data['password'],
        prompt_exchange_code=True,
        delete_existing_device_auths=True,
        **device_auth_details
    ),
    status=data['status'],
    platform=fortnitepy.Platform(data['platform'])
)


@client.event
async def event_device_auth_generate(details: dict, email: str) -> None:
    store_device_auth_details(email, details)


@client.event
async def event_ready() -> None:
    print(crayons.green(f'[PartyBot] [{time()}] Client ready as {client.user.display_name}.'))

    for pending in client.pending_friends:
        friend = await pending.accept() if data["friendaccept"] else await pending.decline()
        if isinstance(friend, fortnitepy.Friend):
            print(f"[PartyBot] [{time()}] Demande d'amis accepte : {friend.display_name}.")
        else:
            print(f"[PartyBot] [{time()}] Demande d'amis refuse : {pending.display_name}.")


@client.event
async def event_party_invite(invite: fortnitepy.PartyInvitation) -> None:
    await invite.accept()
    print(f'[PartyBot] [{time()}] Invitation de groupe accepte de: {invite.sender.display_name}.')


@client.event
async def event_friend_request(request: fortnitepy.PendingFriend) -> None:
    print(f"[PartyBot] [{time()}] Demande d'amis recue de : {request.display_name}.")

    if data['friendaccept']:
        await request.accept()
        print(f"[PartyBot] [{time()}] Demande d'amis accepte : {request.display_name}.")
    else:
        await request.decline()
        print(f"[PartyBot] [{time()}] Demande d'amis refuse : {request.display_name}.")

@client.event
async def event_friend_message(message: fortnitepy.FriendMessage) -> None:
    args = message.content.split()
    split = args[1:]
    content = " ".join(split)

    print(f'[PartyBot] [{time()}] {message.author.display_name}: {message.content}')

    if "!skin" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.TYPE, 'Outfit')
        )

        if cosmetic is None:
            await message.reply(f"Le skin {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] Le skin {content} n'a pas ete trouve.")
        else:
            await message.reply(f'Le skin {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] Le skin {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_outfit(asset=cosmetic.id)

    elif "!sac" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.TYPE, 'Back Bling')
        )

        if cosmetic is None:
            await message.reply(f"Le sac {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] Le sac {content} n'a pas ete trouve.")
        else:
            await message.reply(f'Le sac {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] Le sac {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_backpack(asset=cosmetic.id)

    elif "!emote" in args[0].lower():
        await client.user.party.me.clear_emote()

        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.TYPE, 'Emote')
        )

        if cosmetic is None:
            await message.reply(f"L'emote {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] L'emote {content} n'a pas ete trouve.")
        else:
            await message.reply(f'L\'emote {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] L'emote {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_emote(asset=cosmetic.id)

    elif "!pioche" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.TYPE, 'Harvesting Tool')
        )

        if cosmetic is None:
            await message.reply(f"La pioche {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] La pioche {content} n'a pas ete trouve.")
        else:
            await message.reply(f'La pioche {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] La pioche {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_pickaxe(asset=cosmetic.id)

    elif "!pet" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.BACKEND_TYPE, 'AthenaPet')
        )

        if cosmetic is None:
            await message.reply(f"Le pet {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] Le pet {content} n'a pas ete trouve.")
        else:
            await message.reply(f'Le pet {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] La pioche {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_pet(asset=cosmetic.id)

    elif "!emoji" in args[0].lower():
        await client.user.party.me.clear_emote()

        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.BACKEND_TYPE, 'AthenaDance')
        )

        if cosmetic is None:
            await message.reply(f"L'emoji {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] L'emoji {content} n'a pas ete trouve.")
        else:
            await message.reply(f'L\'emoji {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] L'emoji {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_emoji(asset=cosmetic.id)

    elif "!trainee" in args[0].lower():
        cosmetic = await BenBotAsync.get_cosmetic(
            content,
            params=BenBotAsync.Tags.NAME,
            check=(BenBotAsync.Filters.TYPE, 'Contrail')
        )

        if cosmetic is None:
            await message.reply(f"La trainee {content} n'a pas ete trouve.")
            print(f"[PartyBot] [{time()}] La trainee {content} n'a pas ete trouve.")
        else:
            await message.reply(f'La trainee {cosmetic.displayName} a ete selectionne.')
            print(f"[PartyBot] [{time()}] La trainee {cosmetic.displayName} a ete selectionne.")
            await client.user.party.me.set_contrail(cosmetic.id)

    elif "!ghoul" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=1
        )

        await client.user.party.me.set_outfit(
            asset='CID_029_Athena_Commando_F_Halloween',
            variants=variants
        )

        await message.reply('Le skin Ghoul Trooper a ete selectionne')

    elif "!renegade" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=1
        )

        await client.user.party.me.set_outfit(
            asset='cid_028_athena_commando_f',
            variants=variants
        )

        await message.reply('Le skin Renegade Raider a ete selectionne')

    elif "!recon" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=1
        )

        await client.user.party.me.set_outfit(
            asset='cid_022_athena_commando_f',
            variants=variants
        )

        await message.reply('Le skin Recon Expert a ete selectionne')

    elif "!bot" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=1
        )

        await client.user.party.me.set_outfit(
            asset='cid_vip_athena_commando_m_galileogondola_sg',
            variants=variants
        )

        await message.reply('Le skin Bot a ete selectionne')

    elif "!banner" in args[0].lower():
        await client.user.party.me.set_banner(icon=args[1], color=args[2], season_level=args[3])

        await message.reply(f'La banniere a ete modifiee: {args[1]}, {args[2]}, {args[3]}.')
        print(f"[PartyBot] [{time()}] La banniere a ete modifiee: {args[1]}, {args[2]}, {args[3]}.")

    elif "cid_" in args[0].lower():
        if 'banner' not in args[0]:
            await client.user.party.me.set_outfit(
                asset=args[0]
            )
        else:
            await client.user.party.me.set_outfit(
                asset=args[0],
                variants=client.user.party.me.create_variants(profilebanner='ProfileBanner')
            )

        await message.reply(f'Skin set to {args[0]}')
        await print(f'[PartyBot] [{time()}] Skin set to {args[0]}')

    elif "vtid_" in args[0].lower():
        vtid = await set_vtid(args[0])
        if vtid[1] == 'Particle':
            variants = client.user.party.me.create_variants(particle_config='Particle', particle=1)
        else:
            variants = client.user.party.me.create_variants(**{vtid[1].lower(): int(vtid[2])})

        await client.user.party.me.set_outfit(asset=vtid[0], variants=variants)
        await message.reply(f'Variants set to {args[0]}.\n'
                            '(Warning: This feature is not supported, please use !variants)')

    elif "!variants" in args[0].lower():
        try:
            args3 = int(args[3])
        except ValueError:
            args3 = args[3]

        if 'cid' in args[1].lower() and 'jersey_color' not in args[2]:
            variants = client.user.party.me.create_variants(**{args[2]: args[3]})
            await client.user.party.me.set_outfit(
                asset=args[1],
                variants=variants
            )
        elif 'cid' in args[1].lower() and 'jersey_color' in args[2]:
            variants = client.user.party.me.create_variants(pattern=0, numeric=69, **{args[2]: args[3]})
            await client.user.party.me.set_outfit(
                asset=args[1],
                variants=variants
            )
        elif 'bid' in args[1].lower():
            variants = client.user.party.me.create_variants(item='AthenaBackpack', **{args[2]: args3})
            await client.user.party.me.set_backpack(
                asset=args[1],
                variants=variants
            )
        elif 'pickaxe_id' in args[1].lower():
            variants = client.user.party.me.create_variants(item='AthenaPickaxe', **{args[2]: args3})
            await client.user.party.me.set_pickaxe(
                asset=args[1],
                variants=variants
            )

        await message.reply(f'Set variants of {args[1]} to {args[2]} {args[3]}.')
        print(f'[PartyBot] [{time()}] Set variants of {args[1]} to {args[2]} {args[3]}.')

    elif "!checkeredrenegade" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=2
        )

        await client.user.party.me.set_outfit(
            asset='CID_028_Athena_Commando_F',
            variants=variants
        )

        await message.reply('Skin set to Checkered Renegade!')

    elif "!mintyelf" in args[0].lower():
        variants = client.user.party.me.create_variants(
            material=2
        )

        await client.user.party.me.set_outfit(
            asset='CID_051_Athena_Commando_M_HolidayElf',
            variants=variants
        )

        await message.reply('Skin set to Minty Elf!')

    elif "eid_" in args[0].lower():
        await client.user.party.me.clear_emote()
        await client.user.party.me.set_emote(
            asset=args[0]
        )
        await message.reply(f'Emote set to {args[0]}!')

    elif "!stop" in args[0].lower():
        await client.user.party.me.clear_emote()
        await message.reply('Stopped emoting.')

    elif "bid_" in args[0].lower():
        await client.user.party.me.set_backpack(
            asset=args[0]
        )

        await message.reply(f'Backbling set to {args[0]}!')

    elif "!help" in args[0].lower():
        await message.reply('For a list of commands, goto; https://github.com/xMistt/fortnitepy-bot/wiki/Commands')

    elif "PICKAXE_ID_" in args[0].lower():
        await client.user.party.me.set_pickaxe(
            asset=args[0]
        )

        await message.reply(f'Pickaxe set to {args[0]}')

    elif "petcarrier_" in args[0].lower():
        await client.user.party.me.set_pet(
            asset=args[0]
        )

        await message.reply(f'Pet set to {args[0]}!')

    elif "emoji_" in args[0].lower():
        await client.user.party.me.clear_emote()
        await client.user.party.me.set_emoji(
            asset=args[0]
        )

        await message.reply(f'Emoji set to {args[0]}!')

    elif "trails_" in args[0].lower():
        await client.user.party.me.set_contrail(asset=args[0])

        await message.reply(f'Contrail set to {args[0]}!')

    elif "!legacypickaxe" in args[0].lower():
        await client.user.party.me.set_pickaxe(
            asset=args[1]
        )

        await message.reply(f'Pickaxe set to {args[1]}!')

    elif "!point" in args[0].lower():
        if 'pickaxe_id' in args[1].lower():
            await client.user.party.me.set_pickaxe(asset=args[1])
            await client.user.party.me.set_emote(asset='EID_IceKing')
            await message.reply(f'Pickaxe set to {args[1]} & Point it Out played.')
        else:
            cosmetic = await BenBotAsync.get_cosmetic(
                content,
                params=BenBotAsync.Tags.NAME,
                check=(BenBotAsync.Filters.TYPE, 'Harvesting Tool')
            )
            if cosmetic is None:
                await message.reply(f"Couldn't find a pickaxe with the name: {content}")
            else:
                await client.user.party.me.set_pickaxe(asset=cosmetic.id)
                await client.user.party.me.clear_emote()
                await client.user.party.me.set_emote(asset='EID_IceKing')
                await message.reply(f'Pickaxe set to {content} & Point it Out played.')

    elif "!ready" in args[0].lower():
        await client.user.party.me.set_ready(fortnitepy.ReadyState.READY)
        await message.reply('Ready!')

    elif ("!unready" in args[0].lower()) or ("!sitin" in args[0].lower()):
        await client.user.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await message.reply('Unready!')

    elif "!sitout" in args[0].lower():
        await client.user.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await message.reply('Vous pouvez lancer le matchmaking! Je vous attend ici')

    elif "!bp" in args[0].lower():
        await client.user.party.me.set_battlepass_info(
            has_purchased=True,
            level=args[1],
        )

    elif "!level" in args[0].lower():
        await client.user.party.me.set_banner(
            icon=client.user.party.me.banner[0],
            color=client.user.party.me.banner[1],
            season_level=args[1]
        )

    elif "!echo" in args[0].lower():
        await client.user.party.send(content)

    elif "!status" in args[0].lower():
        await client.set_status(content)

        await message.reply(f'Le status est maintenant : {content}')
        print(f'[PartyBot] [{time()}] Le status est maintenant : {content}.')

    elif "!leave" in args[0].lower():
        await client.user.party.me.set_emote('EID_Wave')
        await asyncio.sleep(2)
        await client.user.party.me.leave()
        await message.reply('Bye!')
        print(f'[PartyBot] [{time()}] J\'ai quitte comme on me l\'a demande')

    elif "!kick" in args[0].lower():
        user = await client.fetch_profile(content)
        member = client.user.party.members.get(user.id)
        if member is None:
            await message.reply("Je n'ai pas trouve le joueur")
        else:
            try:
                await member.kick()
                await message.reply(f"Utilisateur explusé : {member.display_name}.")
                print(f"[PartyBot] [{time()}] Utilisateur explusé : {member.display_name}")
            except fortnitepy.Forbidden:
                await message.reply(f"Je ne peux pas expulser {member.display_name}, je ne suis pas le chef du groupe.")
                print(crayons.red(f"[PartyBot] [{time()}] [ERROR]"
                                  "Je ne peux pas expulser car je ne suis pas le chef du groupe."))

    elif "!lead" in args[0].lower():
        if len(args) == 1:
            user = await client.fetch_profile(message.author.display_name)
            member = await client.user.party.members.get(user.id)
        else:
            user = await client.fetch_profile(content)
            member = client.user.party.members.get(user.id)

        if member is None:
            await message.reply("Je n'ai pas trouve le joueur")
        else:
            try:
                await member.promote()
                await message.reply(f"Nouveau chef du groupe : {member.display_name}.")
                print(f"[PartyBot] [{time()}] Nouveau chef du groupe : {member.display_name}")
            except fortnitepy.Forbidden:
                await message.reply(f"Je ne peux pas mettre chef {member.display_name}, je ne suis pas le chef du groupe.")
                print(crayons.red(f"[PartyBot] [{time()}] [ERROR]"
                                  "Je ne peux pas mettre chef car je ne suis pas le chef du groupe."))

    elif "playlist_" in args[0].lower():
        try:
            await client.user.party.set_playlist(playlist=args[0])
        except fortnitepy.Forbidden:
            await message.reply(f"Je ne peux pas mettre le mode de jeu {args[1]}, je ne suis pas le chef du groupe.")
            print(crayons.red(f"[PartyBot] [{time()}] [ERROR]"
                              "Je ne peux pas mettre le mode de jeu car je ne suis pas le chef du groupe."))

    elif "!platform" in args[0].lower():
        await message.reply(f'Setting platform to {args[0]}')
        party_id = client.user.party.id
        await client.user.party.me.leave()
        client.platform = fortnitepy.Platform(args[1])
        await message.reply(f'La plateforme est : {str(client.platform)}.')
        try:
            await client.join_to_party(party_id, check_private=True)
        except fortnitepy.Forbidden:
            await message.reply('Failed to join back as party is set to private.')

    elif "!id" in args[0].lower():
        user = await client.fetch_profile(content, cache=False, raw=False)
        try:
            await message.reply(f"L'Epic ID de {content} est: {user.id}")
        except AttributeError:
            await message.reply(f"Je ne peux pas trouver d'Epic ID avec: {content}.")

    elif "!privacy" in args[0].lower():
        try:
            if 'public' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            elif 'prive' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
            elif 'amis' in args[1].lower():
                await client.user.party.set_privacy(fortnitepy.PartyPrivacy.FRIENDS)

            await message.reply(f'La confidentialite du groupe est : {client.user.party.privacy}.')
            print(f'[PartyBot] [{time()}] La confidentialite du groupe est : {client.user.party.privacy}.')

        except fortnitepy.Forbidden:
            await message.reply(f"Je ne peux pas mettre la confidentialité {args[1]} car je ne suis pas le chef du groupe.")
            print(crayons.red(f"[PartyBot] [{time()}] [ERROR]"
                              "Je ne peux pas mettre la confidentialité car je ne suis pas le chef du groupe."))

    elif "!copy" in args[0].lower():
        if len(args) >= 1:
            member = client.user.party.members.get(message.author.id)
        else:
            user = await client.fetch_profile(content)
            member = client.user.party.members.get(user.id)

        await client.user.party.me.edit(
            functools.partial(
                fortnitepy.ClientPartyMember.set_outfit,
                asset=member.outfit,
                variants=member.outfit_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_backpack,
                asset=member.backpack,
                variants=member.backpack_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_pickaxe,
                asset=member.pickaxe,
                variants=member.pickaxe_variants
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_banner,
                icon=member.banner[0],
                color=member.banner[1],
                season_level=member.banner[2]
            ),
            functools.partial(
                fortnitepy.ClientPartyMember.set_battlepass_info,
                has_purchased=True,
                level=member.battlepass_info[1]
            )
        )

        await client.user.party.me.set_emote(asset=member.emote)

    elif "!matchmakingcode" in args[0].lower():
        await client.user.party.set_custom_key(
            key=content
        )

        await message.reply(f'Cle mise à : {content}')

    elif "!ninja" in args[0].lower():
        await client.user.party.me.set_outfit(
            asset='CID_605_Athena_Commando_M_TourBus'
        )

        await message.reply('Skin set to Ninja!')

    elif "!ponpon" in args[0].lower():
        await client.user.party.me.set_emote(
            asset='EID_TourBus'
        )

        await message.reply('Emote set to Ninja Style!')

    elif "!enlightened" in args[0].lower():
        await client.user.party.me.set_outfit(
            asset=args[1],
            variants=client.user.party.me.create_variants(progressive=4),
            enlightenment=(args[2], args[3])
        )

        await message.reply(f'Skin set to {args[1]} at level {args[3]} (for Season 1{args[2]}).')

    elif "!rareskins" in args[0].lower():
        rare_skins = ('CID_028_Athena_Commando_F', 'CID_017_Athena_Commando_M', 'CID_022_Athena_Commando_F')
        await message.reply('Showing all rare skins now.')

        await client.user.party.me.set_outfit(
            asset='CID_030_Athena_Commando_M_Halloween',
            variants=client.user.party.me.create_variants(clothing_color=1)
        )

        await message.reply('Skin set to Purple Skull Trooper!')
        await asyncio.sleep(2)

        await client.user.party.me.set_outfit(
            asset='CID_029_Athena_Commando_F_Halloween',
            variants=client.user.party.me.create_variants(material=3)
        )

        await message.reply('Skin set to Pink Ghoul Trooper!')
        await asyncio.sleep(2)

        for skin in rare_skins:
            await client.user.party.me.set_outfit(
                asset=skin
            )

            await message.reply(f'Skin set to {skin}!')
            await asyncio.sleep(2)

    elif "!goldenpeely" in args[0].lower():
        await client.user.party.me.set_outfit(
            asset='CID_701_Athena_Commando_M_BananaAgent',
            variants=client.user.party.me.create_variants(progressive=4),
            enlightenment=(2, 350)
        )

        await message.reply(f'Skin set to Golden Peely.')


if (data['email'] and data['password']) and (data['email'] != 'email@email.com' and data['password'] != 'password1'):
    try:
        client.run()
    except fortnitepy.AuthException as e:
        print(crayons.red(f"[PartyBot] [{time()}] [ERROR] {e}"))
else:
    print(crayons.red(f"[PartyBot] [{time()}] [ERROR] Failed to login as no (or default) account details provided."))
