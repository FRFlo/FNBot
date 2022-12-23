from dotenv import load_dotenv
from fortnitepy import AdvancedAuth, ReadyState
from fortnitepy.ext import commands
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
    owner_id=os.getenv('OWNER_ID'),
)
bot.add_all_mode = True
bot.owner_only = True

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
    print(f"Connecté en tant que {bot.user.display_name}")
    for friend in bot.incoming_pending_friends:
        await friend.accept()


@bot.event
async def event_friend_request(request):
    try:
        await request.accept()
    except:
        pass


@bot.event
async def event_party_invite(invitation):
    if await bot.is_owner(invitation.sender.id):
        await invitation.accept()
        await bot.party.me.set_ready(ReadyState.SITTING_OUT)
        if bot.add_all_mode:
            success = []
            failed = []
            for member in invitation.party.members:
                try:
                    await member.add()
                    success.append(member.display_name)
                except:
                    failed.append(member.display_name)
            print(f"Amis ajoutés ({len(success)}): {', '.join(success)}")


@bot.event
async def event_party_member_join(member):
    if bot.add_all_mode:
        try:
            await member.add()
            print(f"Amis ajoutés: {member.display_name}")
        except:
            pass

bot.run()
