from dotenv import load_dotenv
from fortnitepy import AdvancedAuth, ReadyState, OutgoingPendingFriend
from fortnitepy.ext import commands
from lib import Color
import com
import json
import os
load_dotenv()


def get_auth_details():
    if os.path.isfile('auths.json'):
        with open('auths.json', 'r') as f:
            return json.load(f)
    else:
        return {}


bot = commands.Bot(
    command_prefix='!',
    auth=AdvancedAuth(
        email=os.getenv('EMAIL'),
        password=os.getenv('PASSWORD'),
        prompt_authorization_code=True,
        prompt_code_if_invalid=True,
        delete_existing_device_auths=True,
        **get_auth_details().get(os.getenv('EMAIL'), {})
    ),
    status="BOXFIGHT, BIOS ZONE WARS, FFA, BOX PVP",
    owner_ids=os.getenv('OWNER_IDS'),
)
bot.add_all_mode = False
bot.owner_only = True
bot.research_mode = False

bot.add_cog(com.PartyCommands(bot))
bot.add_cog(com.CosmeticCommands(bot))
bot.add_cog(com.MiscCommands(bot))


@bot.event
async def event_device_auth_generate(details, email):
    existing = get_auth_details()
    existing[email] = details

    with open('auths.json', 'w') as fp:
        json.dump(existing, fp, indent=4)


@bot.event
async def event_ready():
    for friend in bot.incoming_pending_friends:
        await friend.accept()
    for friend in bot.outgoing_pending_friends:
        await friend.cancel()
    print(f"{Color.GREEN}Connecté en tant que {bot.user.display_name} ({bot.user.id})")


@bot.event
async def event_friend_request(request):
    if isinstance(request, OutgoingPendingFriend):
        print(
            f"{Color.BLUE}[Amis] {Color.LIGHT_BLUE}Demande envoyée à {request.display_name} ({request.id})")
    else:
        await request.accept()
        print(
            f"{Color.BLUE}[Amis] {Color.LIGHT_BLUE}Demande acceptée de {request.display_name} ({request.id})")


@bot.event
async def event_party_invite(invitation):
    if await bot.is_owner(invitation.sender.id):
        await invitation.accept()
        print(
            f"{Color.RED}[Groupe] {Color.LIGHT_RED}Invitation acceptée de {invitation.sender.display_name} ({invitation.sender.id})")
        if bot.add_all_mode:
            for member in invitation.party.members:
                try:
                    await member.add()
                except:
                    pass


@bot.event
async def event_party_member_join(member):
    if member.id == bot.user.id:
        print(f"{Color.RED}[Groupe] {Color.LIGHT_RED}Rejoint la partie de {bot.party.leader.display_name} ({bot.party.leader.id}): {bot.party.member_count} membre(s)")
        try:
            await bot.party.me.set_ready(ReadyState.SITTING_OUT)
        except:
            pass
        return
    if bot.add_all_mode:
        try:
            await member.add()
        except:
            pass

bot.run()
