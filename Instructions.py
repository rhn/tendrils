"""
Instructions for playing Tendrils.  These use some markup tags (see Utils.py for markup
docs).  These are displayed from the welcome screen and from the maze screen.
"""
from Constants import *


ReleaseNotes = """<CENTER><CN:BRIGHTGREEN><BIG>Tenrdrils: Beta Release %s</BIG></C>

"This Game...requires one Player, <CN:ORANGE>at least</C>.  I am not aware of any Game that can be played \
with <CN:ORANGE>less</C> than this number: while there are several that require <CN:ORANGE>more</C>: take Cricket, \
for instance, which requires twenty-two.  How much easier it is, when you want to play a Game, to find \
<CN:ORANGE>one</c> player than twenty-two.  At the same time, though one Player is enough, a good deal more \
amusement may be got by two working at it together, and correcting each other's mistakes."
<CN:GREY>- Lewis Carroll, Game of Logic</C>

Welcome to Tendrils: The Role-playing Remix.  Tendrils is a game made out of bits and pieces \
of other games.  So, many things will look and sound very familiar...  Combat is resolved with \
a rhythm game, similar to the Bemani series.  There are also various mini-games played to unlock \
treasure chests.  We hope you will enjoy the game.  The source code is included, so if you want \
to poke around in it, or even make Tendrils II: Electric Boogaloo, you're free to do so. 

"<CN:ORANGE>DANCE OR DIE!!!</C>" <CN:GREY>- Topo, Brave Fencer Musashi</C>

"""%Version

HelpText = """<CENTER><CN:BRIGHTBLUE><BIG>Tendrils</BIG></c></Center>

Welcome to <CN:BRIGHTGREEN>Nexus</C>, the conjunction world.  Portals from a thousand worlds lead to Nexus, making \
it an exciting and chaotic place.  You have made your living as a merchant-at-arms, guarding trade caravans to \
and from exotic lands.  Lately, however, the portals out of Nexus have been closing, and groups of monsters have \
overrun several towns.  Your quest is to destroy this scourge at its root, deep in the uncharted Dungeons of \
Nexus.

Use the <CN:green>arrow keys</c> to move around the maze.  (Up moves forward, Left and Right \
turn, and Down turns around).  Press the <CN:green>space bar</c> to open doors. 

Press 1-4 to select members of your party (or click on their names in the status panel).  Use the mouse or keyboard shortcuts \
to cast spells, check equipment, and use items.  For instance, if you have a clearic in slot 3, you could press 3, then C, then A \
to cast the Cure spell.  (Healing spells are important for dungeon survival)

From the maze, you press <CN:green>I</c> \
to open inventory screen, where you can also check on your characters' \
attributes.

The first thing to do is talk to all the people in town, and go shopping \
for the best equipment you can find.  

When you get into battle, watch the arrow panel on the left side of the screen.  Swords and \
shields will fly upward in synch with the music.  Hit the matching arrow key just as \
the icons cross the white line at the top - this makes your characters dodge, and attack. \
The better your timing, the better your party fights.  \
If you get wounded, pause by hitting ESCAPE, and have one of your characters <CN:red>Use</c> \
a <CN:BLUE>Potion</c> or <CN:red>Cast</c> the spell of <CN:blue>Cure</c>.

<CN:BRIGHTGREEN>Hint:</c> Before leaving town, visit the Bard's Guild to practice combat! 

Watch for chests.  Chests hold items, but \
most of them are trapped!  There are various locks, each with a different mini-game to disarm it; \
having a <CN:RED>Ninja</C> \
in your party makes unlocking chests much easier.

Once you win a battle or two, head back to town to rest at the <CN:green>inn</c> and save \
the game at the <cn:green>save shrine</c>.  Making a <CN:BRIGHTBLUE>map</C> on grid paper \
is highly recommended.  The dungeon is full of treasure, danger, monsters and puzzles. \
Good luck, and have fun.

<CN:BRIGHTBLUE>Now go!  And smite the foul beasts with your burning rhythm!</c>

<CN:BRIGHTGREEN>Yrs Truly,
 --- The Game Designers</C>
"""

DanceInstructions1 = """<center>Welcome to the Bard's Guild.</center>

Here is a quick lesson in how Tendrils combat works:  
On the left, <CN:BRIGHTRED>swords</c> and <CN:BRIGHTBLUE>shields</C> will scroll up from \
the bottom of the screen.  You need to press the <CN:BRIGHTRED>arrow keys</C> just as the \
swords and shields cross the <CN:BRIGHTRED>critical line</C>.

Press the arrow that points in the correct direction.  If the sword is pointing <CN:BRIGHTGREEN>up</c>, \
you must hit the <CN:BRIGHTGREEN>up</c> arrow.  (Or if you are using a <CN:BRIGHTGREEN>dance pad</C>, you \
must step on the <CN:BRIGHTGREEN>up</c> arrow)

Each direction corresponds to a member of your party.  For each sword pointing their way, they \
<CN:GREEN>attack</c>!  For each shield pointing their way, they <CN:BLUE>defend</c>!  If your \
timing is good on swords, your attacks will hit more often and do more damage.  If your timing \
is good on shields, you will dodge more often, and take less damage from monsters.  Good arrow timing \
also gives you an <CN:GREEN>experience point bonus</c>.
"""

DanceInstructions2 = """<center>Combat (continued)</center>

An arrow that appears in a multi-colored swath is a <CN:BRIGHTGREEN>freeze</C> arrow.  You should hold \
the direction down for as long as the arrow lasts.

You can pause battles at any time by hitting <CN:RED>Escape</c>.  This is useful if you need to \
take a break, or if you want to do something fancy like <CN:Green>use</c> an item or <CN:green>cast</c> \
a spell.  

A <CN:YELLOW>bard</c> can influence which battle-song is played; bards with a high CHA can even \
slow down the pace of a song to make it easier to hit all the arrows.  In addition, the bard's song \
allows your spell-casters to slowly regenerate <cn:BRIGHTBLUE>mana</c> as you walk around the maze. \
Bards can be very useful!"""

DanceInstructions3 = """Now you are ready to practice a little.   Hit the corresponding arrow key just as the \
swords cross the critical line.  For freeze arrows, <CN:GREEN>hit and hold</c> the arrow when the sword crosses the \
critical line.  Click the button below when you are done practicing.
"""

InnInstructions = """<CENTER>Inn</CENTER>

Sleeping at an inn recovers hit points (<CN:RED>HP</C>) and mana (<CN:BLUE>MP</C>), and cures \
problems like <CN:PURPLE>poison</C>.  Inns will become more expensive after you raise your level.

Hover the mouse pointer over a character to see their stats.  You can also recruit more characters to \
swap in and out of your party.  Click a character to select, \
then click a second character to swap positions.

(Remember to <CN:GREEN>visit the save shrine</C> north of the inn to <CN:GREEN>save your game</c>, too!)"""

ShopInstructions = """<CENTER>Shopping</CENTER>

Shop inventory is listed on top.  Click a shop item to buy it.  Your party's items are listed on the \
bottom.  Click an item to sell it.  (Shopkeepers charge more for items than they are willing to pay)

The buttons at bottom right let you filter the view to only one item-type (e.g. weapons) at once.

<CN:BRIGHTGREEN>Tip</C>: Buy plenty of potions.  You can use them in battle or in the maze to recover hit points.
"""

TendrilsText = [""]

# Level 1
TendrilsText.append("""<CENTER><CN:ORANGE>High-speed RPG</c></CENTER>

High-speed RPG is a way to create sensory overload out of ordinary household objects.  You will need:
- An <CN:RED>emulator</c> with quicksave/quickload and a frameskip ("fast-forward") key.  ZSNES or VisualBoy Advance will do nicely. 
- Five or more <CN:RED>RPG roms</c>
- An <CN:RED>alarm program</C> or, for the truly old-school, an <CN:RED>egg-timer</C>

Set the alarm to go off in five minutes.  Start playing the first RPG, making liberal use of the fast-forward button to walk from place to place and to rush routine battles.   When the alarm goes off, quicksave and immediately start the next game.  Keep going.  When you finish with the last RPG on the list, wrap back around to the first, quickload, and carry on.

Remembering what's happening in which game ("Was I going east to save the princess, or going south to kill the demon?") is part of the challenge.  

Enjoy.""")
# Level 2
TendrilsText.append("""<CN:BRIGHTGREEN>O</C> Random Number Generator,
Father of critical hit tables
Mother of all treasure drops
Thou spinnest like a great cheese wheel
First gouda is on top
And then sharp cheddar is ascendant

<CN:BRIGHTGREEN>When</C> lady Fortune smiles
Even mosquitos drop treasure chests
When she is angry 
Who can make their saving throws?

<CN:BRIGHTGREEN>Fools</C> blow on the dice
Rattle the platonic solids
To them the future is hidden
Behind the DM's screen

<CN:BRIGHTGREEN>The</C> wise man learns a way
To reset the system clock
He knows how to step twice
Into the same number stream""")

# Level 3
TendrilsText.append("<CENTER><IMG:killyou>")

# Level 4
TendrilsText.append("""<CENTER><BIG>Wiznaibus</BIG></CENTER>

Once a FF:Tactics character gains access to the Dancer job, you can \
use an attack called <CN:ORANGE>Wiznaibus</c>.  Pronounced, naturally \
enough, "Whiz-nay-bus".  But after a while, it may dawn on you that \
the dance's name is wrong.  The name has gone from English to Japanese \
and back again; it should be "with knives".

The word <CN:ORANGE>wiznaibus</c> is too wonderfully painful not to \
re-use.  And so, when translations are so incompetent that they \
accidentally become hilarious...that is <CN:ORANGE>wiznaibus</C>. \
When voice acting is so bad that it makes you cringe...that is \
<CN:ORANGE>wiznaiubus</c>.

Game localization is a tough job, and <CN:ORANGE>wiznaibus</c> doesn't \
refer to garden-variety lapses.  No, we reserve <CN:ORANGE>wiznaibus</c> to refer to \
mistakes that betray a total lack of respect for the audience, and the \
authors, and the work itself.  When Castlevania II says<CN:GREEN>YOU \
NOW P</C><CN:BRIGHTRED>R</C><CN:GREEN>OSESS DRACULA'S RIB</C>, that is \
<CN:ORANGE>wiznaibus</C>.  When Chrono's party wakes up with a \
hangover after drinking too much "soup", that is \
<CN:ORANGE>wiznaibus</c>.  The voice acting in Resident Evil is so \
<CN:ORANGE>wiznaibus</c> that it's no longer funny.

Thankfully, <CN:ORANGE>wiznaibus</c> is now becoming more the \
exception to the rule.  And so, grizzled old gamers can look back with \
more fondness than frustration on the deranged dialog of yesteryear. 
""")

# Level 5
TendrilsText.append("""He started by writing out his stats.  \
He carefully assessed his wisdom, appraised his dexterity, peered into \
the mirror and ranked his own charisma.  Then he began quantifying his \
skill level in various tasks.  As he boiled pasta, he mentally checked \
his Cooking skill.  As he filled out a crossword, he imagined a series \
of Knowledge skill checks.  It began as an idle mental exercise.  This \
would change, in time, for the worse.

After his girlfriend dumped him, he bought a fresh pad of note paper.  It \
was time to get organized.  He wrote out the names of people he knew, and ranked their disposition \
toward them with a little row of <CN:RED>valentine hearts</C> (for good) or \
<CN:PURPLE>frowning skulls</C> (for bad).  He chose Christmas gifts for everyone \
by rolling against a table (incorporating modifiers for the recipient's \
class and statistics). 

His apartment became tidier and tidier as this process went on.  Washing \
the dishes was no longer a chore, but a source of experience points - and \
a boost to his Lawful alignment...""")

# Level 6
TendrilsText.append("""<CENTER><CN:BRIGHTGREEN>How To Chiyochiyo</C></CENTER>

<CN:ORANGE>Stage 1</C>
- Pass stage 1 of <CN:GREEN>Rai Den</C> in one life, <CN:YELLOW>and</c>
- Reach stage 5 of <CN:GREEN>Galaga</C>, <CN:YELLOW>and</C>
- Score at least 60,000 points in <CN:GREEN>Twin cobra</c>

<CN:ORANGE>Stage 2</C>
- Eat all 4 <CN:GREEN>Pac-Man</c> ghosts using one power pellet, <CN:YELLOW>or</c>
- Get the EXTRA bonus in <CN:GREEN>Mr. Do!</c>, <CN:YELLOW>or</c>
- Get the EXTEND bonus in <CN:GREEN>Bubble Bobble</c>, <CN:YELLOW>or</c>
- Get the EXTRA bonus in <CN:GREEN>Cutie-Q</c>

<CN:ORANGE>Stage 3</C>
- Finish <CN:GREEN>Shinobi</C> with 1 continue, <CN:YELLOW>or</c>
- Finish <CN:GREEN>Black Tiger</C> with 1 continue, <CN:YELLOW>or</c>
- Finish <CN:GREEN>Rastan</C> with 1 continue

<CN:ORANGE>Stage 4</C>
<CN:GREY>...to be continued!</C>
""")

# Level 7
TendrilsText.append("""<big><CN:BRIGHTrED>Over 500 classes!</C></big>
There are 300 playable races - including 50 flavors of elf, such as \
Wood Elves, High Elves, Dark Elves, Grey Elves, and Cheese Elves. \
Available skills include archery, swordsmanship, swimming, dancing, \
farming, shield repair, woodchuck ranching, goblin lore, squirrel \
languages, moving silently, moving noisily, trap detection, \
alphabetizing, vorpal strike, bird calls, kung fu, and breathing.  (Be \
sure to invest skill points in Breathing; on a critical failure, your \
character will fall unconscious and require someone with the \
Resuscitate skill to revive him!)

<big><CN:BRIGHTrED>50-person party!</c></big>
As you can see from the screenshots, the retinue following the leader \
stretches all the way from the first town to the first dungeon. \
Customize party marching order, attack formation, and hairstyle! Every \
male character has a dark and troubled past, and every female \
character has wonderbra battle armor!

<big><CN:BRIGHTrED>Thousand-level dungeon!</c></big>
Quit your job and stock up on graph paper and benzedrine, because the \
new dungeon has over 1,000 levels! Along the way, your characters will \
reach experience level 800 or so.  A maxxed-out archer carries a \
repeating crossbow that fires small trees, and a maxxed-out wizard can \
summon a supernova (note: fire resistance is recommended before \
casting this spell!)

<big><CN:BRIGHTRED>Immense plot!</c></big>
In your travels, you'll ferret out clues from towns with populations \
of 500 or more people.  The full quest includes 3,000,000 words of \
dialog, nearly all of which are spelled correctly! 

<big><CN:BRIGHTrED>Full equipment system!</c></big>
The new equipment slots include body armor, cloak, arms, hands, feet, \
each finger (with polydactyly as an option, costing 2 creation \
points), each toe, anklets, left and right nostrils, belt, bra (female \
characters only), tattoo, monocle, butt, eyebrow-piercing, and hat.

<big><CN:BRIGHTrED>Ultimate Boss!</c></big>
The final boss has 12 different forms, and the last battle requires \
approximately 5 hours.  Bring plenty \
of potions of extra extra extra healing!
""")


#Level 8
TendrilsText.append("""<center><IMG:giantspider>

A truly <CN:BRIGHTRED>giant</C> spider attacks Bree...""")

#Level 9
TendrilsText.append("""Video Games Will Play You For a Fool!

You've probably heard the stories on the news: Video games lead to \
violence.  The video game makers try to dodge these charges.  Some have \
even attempted to pin the blame for violent crime on drug abuse, or on \
broken homes.  Yeah, right!  I think they'd like us to forget the upsurge \
in bulimia that followed the release of Pac-Man, and all the concussions \
sustained when children trying to be "just like Mario" tried to smash bricks \
with their heads.  

As a recovering "gamer", I can tell you that these allegations are \
completely true.  Many's the time my droogs and I geared up for a night \
of ultraviolence by playing Bubble Bobble.  People may say that young \
people can draw a distinction between fantasy and reality, but at the \
time I was completely convinced that I was a green bubble-blowing dragon, \
able to jump five times my own height.  

A person can only clear so many Tetris rows before he snaps, and the next \
thing you know, he's throwing Molotov cocktails at his own grandmother.

Or just look at Railroad Tycoon 3.  Just the other day, I sent traffic \
through carrier C instead of carrier B, at a higher cost, just to drive \
down B's stock price in preparation for a hostile takeover!  After \
playing, I had to take a look in the mirror and ask: Is this what I have \
become?  Is this really me?

Yes, video games - especially Dance Dance Revolution and Roller Coaster \
Tycoon - cause violence.  

Even unplugging the game console is no escape.  Kids may turn to \
"chess" - which is nothing more than a celebration of regicide - or to \
"go fish", an ecologically unsound game where the objective is to deplete \
all fishing stocks.  

That's why constant vigilance is important.  Check for callouses on your \
children's thumbs, which may be developed by so-called "gamepads".  Check \
around the television for hand-drawn maps with labels like "Potion Shop" \
and "Elf Waterfall".  These are another warning sign.  

If we are careful, and if new government safeguards can be put in place, \
then we needn't see any more young lives cut short by The Sims or \
Bejeweled. """)

#Level 10
TendrilsText.append("""<CN:GREY>From the original Tendrils FAQ, circa 1997:</c>
[2.4.3] How do I find Ernest Namingway?
 
 This is the first really hard part.  You must visit the moon.  Go to Rutz \
 with your airship (which used to be a submarine, which used to be a ship, \
 which used to be a skiff).  It will be converted into a giant robot! \
 Take the giant robot to the Teardrop Tower.  There, your giant robot will \
 be able to get into the cockpit of the EXTRA-GIANT robot, and pilot \
 it around.  Then go to Death Mountain, where your EXTRA-GIANT robot \
 gets into the MEGA-GIANT robot, and pilots it around!  Now you are \
 ready to take off! 

 As you fly up into space, you pass the tank from Blaster Master (which \
 is in hover mode), a cow (from Earthworm Jim), and Jax, who was punched \
 into space earlier (see section 2.3.1).""")