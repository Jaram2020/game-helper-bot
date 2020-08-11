import os, json, re
import discord, asyncio

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib import parse

app = discord.Client()


json_data = open(os.getcwd() + "/token/.config.json", encoding='utf-8').read()
config_json = json.loads(json_data)
token = config_json["token"]

@app.event
async def on_ready():
    print('Logged in as')
    print(app.user.name)
    print(app.user.id)
    print('------')
    game = discord.Game("Game Helper | !help")
    await app.change_presence(status=discord.Status.online, activity=game)


@app.event
async def on_message(message):
    if message.content == "!owsearch":
        embed = discord.Embed(title="Overwatch 점수 검색", description="'배틀태그#숫자' 형식으로 입력해주세요.", color=0x82CC62)
        embed.set_image(url="https://bnetcmsus-a.akamaihd.net/cms/blog_header/q4/Q4K237E1EGPI1467079634956.jpg")

        await message.channel.send(embed=embed)

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:    
            m = await app.wait_for('message',timeout=25.0, check=check)
        except asyncio.TimeoutError:
            await message.channel.send("시간초과!")
        else:
            battletag_bool = bool(re.search('.[#][0-9]', m.content))
            if battletag_bool:
                battletag = m.content.replace("#", "-")
                async with message.channel.typing():
                    req = Request("https://playoverwatch.com/ko-kr/career/pc/" + parse.quote(battletag))
                    res = urlopen(req)

                    bs = BeautifulSoup(res, "html.parser")
                    roles = bs.findAll("div", attrs={"class": "competitive-rank-tier"})
                    scores = bs.findAll("div", attrs={"class": "competitive-rank-level"})
                    public_status = bs.findAll("p", attrs={"class": "masthead-permission-level-text"})
                    comp_data = bs.find("div", attrs={"id": "competitive","data-mode": "competitive"})
                    heroes = comp_data.findAll("div", attrs={"class": "ProgressBar-title"})
                    play_time = comp_data.findAll("div", attrs={"class": "ProgressBar-description"})
                    comp_heroes = []
                    for h in heroes:
                        comp_heroes.append([h])
                    
                    for i in range(len(play_time)):
                        comp_heroes[i].append(play_time[i])


                competitive_roles = [i.get("data-ow-tooltip-text") for i in roles[:len(roles)//2]]
                competitive_score = [i.text for i in scores[:len(scores)//2]]

                if not public_status:
                    await message.channel.send("프로필이 존재하지 않습니다. 배틀태그와 뒤에 숫자를 다시 확인해 주세요.")
                else:
                    if public_status[0].text == "비공개 프로필":
                        await message.channel.send("비공개 프로필입니다. 프로필 공개 설정을 공개로 바꾼 뒤에 사용해 주세요.")
                    else:
                        score_result = ""
                        top_five_result = ""
                        top_five = [[d[0].text, d[1].text] for d in comp_heroes] if len(comp_heroes) <= 5 else [[d[0].text, d[1].text] for d in comp_heroes[:5]]

                        def format_time(s):
                            t = s.split(":")
                            if len(t) == 2:
                                # MM:SS
                                return "{0} 분".format(str(int(t[0])))
                            elif len(t) == 3:
                                # HH:MM:SS
                                return "{0} 시간".format(str(int(t[0])))
                            else:
                                return "0 분"

                        if len(competitive_roles) == 0 and len(competitive_score) == 0:
                            score_result = "아직 배치를 덜본것 같군요! 점수가 없습니다."
                        else:
                            for i in range(len(competitive_roles)):
                                score_result = score_result + competitive_roles[i] + " : " + competitive_score[i] + "\n"
                            score_result = score_result + "입니다."
                        
                        for i, h in enumerate(top_five):
                            top_five_result += "{0}. {1}: {2}\n".format(str(i+1), h[0], format_time(h[1]))


                        embed = discord.Embed(title=battletag.split("-")[0] + " 님의 현재 시즌 경쟁전 점수", description=score_result, color=0x82CC62)
                        embed2 = discord.Embed(title="경쟁전 상위 영웅", description=top_five_result, color=0x82CC62)

                        await message.channel.send(embed=embed)
                        await message.channel.send(embed=embed2)
            else:
                # Invalid
                await message.channel.send("배틀태그가 유효하지 않습니다.")

app.run(token)