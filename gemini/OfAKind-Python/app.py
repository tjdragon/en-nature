import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from streamlit_geolocation import streamlit_geolocation

# --- Load environment variables and configure Gemini ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

# --- Model Configuration (with Temperature) ---
generation_config = genai.GenerationConfig(
    temperature=0.7,
)

model = genai.GenerativeModel('gemini-2.0-flash')

# --- Load System Prompt ---
with open("prompt-2.txt", "r") as f:
    system_prompt_template = f.read()

# --- Restaurant List (Placeholder - Replace or load from file/DB) ---
restaurant_list = ["Jose Andres Restaurants","Parker Hospitality","Above Board","Gravity Heights","Street Guys Hospitality","Strangebird Hospitality","Hoffbrau Steak & Grill House","Noble 33","Maty's","The Urban Oyster","TRIUNE","The Powder Room Champagne Bar","Mishik","Zola","Marco's","Mission Ceviche","Summa House","Farm & Fork Kitchen","Ninepin Hospitality","Apero","Stiggs Brewing Company","Gregory Gourdet Restaurants","Talea","Oseyo","Bronze","Botanica","Nudibranch","Claro","Andora","Hook Hall","CVRG","Killiney Kopitiam","Zinc Port Douglas","Stephen's on State","Matthew Kenney","etta","Bayan Ko Diner","Rize + Rest","Southern Proper Hospitality Group","Luna Italian Cuisine","Marsanne","Andreas Prime Steaks & Seafood","MoMo Paradise","Adalina","Del Alma","Wu Chow/Swift's Attic","Garrett Hospitality","City Winery","Wood & Water","The Bistro on Sterling","Quince","Popei’s Clam Bar","Marylou","Pardon My French + Bakery","Edible Beats","Sacro","B Hospitality Group","CIEL","Vamos","Nina May & Opal","FIG & OLIVE","Singh's Kitchen","Talulla Cambridge","City Post Chophouse","1308 Chicago","Aviation Rooftop Bar & Kitchen","Winston's","Noe Sushi Bar","Centro Mexican Kitchen","Le Pigeon","Bramàre","Rosebud Restaurants","DanDan","Ellē + Tigerella","Woodland","Traveler Street Hospitality","Cecily","Boujis Group","Table25 Fork and Wine","Knead Hospitality","Whaley's","Fiorella","Pubbelly Sushi Pembroke Pines ","Popi's Oysterette","Delicious Hospitality Group","Ella Funt","Field Guide","Amor Wine + Tapas ","Maketto","Tarallucci e Vino","Nômadé","Brickhouse Cafe","Parlay Sporting Club + Kitchen","Le Bon Nosh","Bacchanal","Wooden City","Pubbelly","L'antica Pizzeria da Michele","Mr. Capri","Fallow's Rest Wild","Etta AYA","Bar Vinazo","Mon Ami","Leitao","Durango Cantina","The Crossing Steakhouse ","50 Eggs Hospitality Group","Ambrogio15 Phoenix","Botanical Group","Oceano Kitchen","Chak","Blue Operations","The Regional","Jacques","Crown Restaurant Group","Sushi By Bou","S.K.Y.","Gotham","Knife Steakhouse","Principe","Xiquet","Blackfoot Hospitality","Humble Pie","Barberio Osteria","Carne Gaston","Nomé ","Revolucion Cantina ","Perle","Glorietta + Glory Days","Gem Wine & Gem Home","Sticky Fingers Diner","Lago by Fabio Viviani","Musket Room","The Electric Jane","Artango Bar & Steakhouse","Hamrock's Restaurant","Wow Wow Açaí Bowls • Smoothies • Lemonade","Pop's Bagels","Sauce Queen Kitchen & Pantry","Church Bar","Della Coffee","Nellys Taqueria","Jurassic Magic Coffee","The Ruby Hotel & Bar","Lock & Key","Avli","Provecho","Finch & Pine","Idylwood Grill & Wine Bar","Saltwater Oyster Depot","Regards","Maggie's Farm","Levels","RED O","Abejas","Osteria Bianchi","Jaguar Restaurant","Nightshade Noodle Bar","SAINT","MAÜ","The Warren","Basta Pasta","Catalogue","Se7en","Pepe & Sale","Omakase Restaurant Group","Steep","Purl","Regan Hospitality ","Mother Wolf","Paloma","Prentice Hospitality Group","Eigikutei","The Market District","77 Tapas Inc","Ariete Hospitality","High Road Cycling","MEDI Kitchen + Cocktail","Comoncy","Veggie Grill","Greekman's","Juice Press","Brasserie Brixton","Saucy Chick Goat Mafia","Clara's","Azul","Phorage","Gather Restaurant Group","The Golden Swan","Seabreeze On The Dock","West End Tavern","Spearhead Hospitality","Bevri","Milkshake Concepts","Bar Goa","Serafina","K Pasa","Karne Korean Steakhouse","NoCo Hospitality","Westso Restaurant","Vault Cafe Bar Restaurant ","Mamacita Miami","Lucina","Mirame","Dawn","Boqueria","Sheep By Barashka","Bathtub Gin","Statesman","Campanella","Flex Mussels","New Asia Food Group","Carmel","Ramro","bar56","Casamata","Khmai","Nico’s","Swagyu Burger","The Granola Bar","Loretta & The Butcher","Tiger, Grateful Bread & Solomon's","The Farehouse","EVO","Major Food Group","RMD Group","Stella Hospitality","Leku","Porchetta Hospitality","Ms Chi Cafe","Bill's Supper Club","SubTerra Kitchen & Cellar","KAVIAR Restaurants","Loreto","Mistico","Everything Bar","Pluma by Bluebird Bakery","Parched Hospitality Group","Quarter Acre","CALA","Bachour","Mimo","Juliet Italian Kitchen","Underdog","Cecilia ","Lounge Here","Henry’s Majestic","Zinqué","Leah & Louise","G","Companion Hospitality","La Parisienne French Bistro","Petite Cerise","Kitchen + Kocktails by Kevin Kelley","Cru Hospitality","Suprema Provisions","Swahili Village","Salvaje","Bar Spero","ROOH","31THIRTYONE","8 Hospitality","Herb & Wood","Cookie Crumz","Neme Gastro Bar","Nirmal's ","Genuine Hospitality Group","BITES","Magna","The Dive Oyster Bar","Boston Chops","Gertrude's","Filé Gumbo Bar","Ostras | Latin","Cloak and Petal","Salud","Sap Sua","Alex & Co","Lemont Rosebud","Noisette","Cornerstone Restaurant Group","Cultura Subs","The Honey Hole Bistro and Brunch Bar","Little Rascal","Hotel Herringbone","In Hospitality","LouLou","Foraged","Guesthouse | Easy Rider | Mijo","Beity","Livanos Restaurant Group","Sagaponack","Kuba Cabana","L'Orange","Rossoblu","Smith & Mills","Doce Provisions/Social 27","Rêve","Lamia's Fish Market","BYRDI","CalaMillor","KinKan","Lore","Swan & Fox","Senza Gluten by Jemiko","Divino","Union Square Hospitality Group","REYNA","Vernon's Speakeasy","Juniper & Ivy","Elcielo","101 Hospitality","Two Nine","Osteria La Baia","Mägo Restaurant","Le Grand","Proyecto Tulum","Circle Spey Restaurants","Republica Hospitality","Joy by Seven Reasons","Scratch Restaurants","Kali Restaurant","Juliet","Grace Street Coffee Roasters","La Finca Coffee & Bakery","Macaron Bar","Champagnes Kitchen","Bayou Bakery","Rosen's Bagels","Laurie's Pie Bar","Penellie's","Great White","The Sugar Bar","The Farmer’s Cow Calfé & Creamery","Cabana Club","St Arnold's + Tyber Bierhaus","Hotel Chantelle","Anvil Brewing","Sucker Punch","Colette","Dick & Janes","Kay Rico Coffee","Quince Coffee House","Revolucion Coffee","Cafe Eleven ","Williamsburg Comedy Club","BrewRiver Creole Kitchen","UM.MA","Agnes","Milano's Pizzas","Cheebo ","El Rancho Grande","Kitchen 18","Nayar Taqueria Inc.","El Rincon Mexican Kitchen & Tequila Bar","HopMonk","A la Turka","Block Party Productions","Pita 'Bu","Alma Cocina Latina","Café Deux","Mixtitos Kitchen","Lone Star Taco Bar","Pring NYC","Levantine","138° by Matt Meyer","Saraghina Group","Vandalay Brands","Cafe Habana ","LS Social","Joy Hill","Bar One Lounge","Moreish Hospitality","Bistro 1521","Butcher & the Bear","Gozu","The Penthouse","Élephante","Casa Isola","Norman's","YŪME Hospitality","Caffeine & Dreams Coffee House","Quore","PLG Coffee House and Tavern","Kona","Nomad Donuts","Catania","Reina + Hey ReyRey","Service Bar + Causa","Level 1 Arcade Bar","Pronto Gelato","Cha Cha Matcha","Baker Street","Valley Lodge Tavern","Glaze Teriyaki","Eighteen36","Trellis Gastropub","The Hungry Mule","GAI Chicken & Rice","Ras Plant Based","Andres Carne de Res","Not Your Average Joe's","Berdenas Fine Coffee & Food","PT Hospitality Group","Paperboy","Heavy Handed","Edie's All Day Café & Bar","II Brothers Grill & Bar","Petralunga","Hijo de su Madre","Cafe Bartique","Willie Mae's","Comal 864","Saucy Brew Works","Broad Street Ballers","The Monk's Kettle","Arona Food Place","Space Smash","DeeJays BBQ Ribs & Grille","Havana Beach","Wholey Granoly","Legion","Expat","Da Picky Vegan","Fish Trap'n","Riviera","Party of 5","Shojo","Australian Hotel Bistro","Rosalia's Kitchen","Whitmans Restaurant Group","Aries Lounge","Gyro Republic Fondren","Ivy & Varley & Studio Salt Lake","Sarabeth's","The Yolk","The Lymbar","Kings of Kobe ","Honest Mary's ","Kokomo’s Restaurant","Sunday Dreamin'","The Babe","Stout's","Uncle Paulie's Deli","Sesamo","Panela","South of the Border","Bango Bowls","Fam Hospitality","Taco Town Mexican Grill","Crack Shack Little Italy","Twisted Croissant","World Wrapps ","Tabu","Stove & Co","Angelina Paris","The B100M","Jrk!","Quito's Restaurant and Bar","Guess Family Barbecue","La Parisienne NYC","Recess","Coperta ","Cinders Pizza // Taste & See Creamery","American Icon Brewery","Buttermilk Eatery","Tacos 1986","Z's Bubble Tea","Claudio’s","Overthrow Hospitality","Paraiso","Haystacks Restaurants","Underdogs Cantina","Untitled Supper Club","Oceans 234","Noble Miami","Ostēr","The Corner Drafthouse","Hudson's On the Bend","Shell Shack","Simply Delicious","Soul Vibez + Cant Believe Its Not Meat","TLC","MITA","Le Central Bistro","Ok Omens","Ceibo","The Clé Group","Ember ATX","Atlas Steak House","Ozumo","FAT MIILK","Doughboy Restaurant Group","Croft Alley","Living Green","Alter Brewing","Rock & Reilly's USC","Common Theory","The Gibson","Brix Haus","Salomay","Cal’s Corner","Ivan Ramen","Death By Tequila","Woon","FH Jerk God","Cheeni","Culinary Creative Group","The Licking","Tonati Mexican Grill","The Conche","Hoexters","Guest House","Back of the House","Fabel","Restaurant Dan Arnold","M Street","Rebel Wine Bar","Estes Ristorante","Public Records","ZOOZ","minibar","Sneaky Possum","DELETE","Freeland Spirits ","Sip + Co","Soul & Smoke","UNCO","The Whale","Bibi Ji","Southern Chicago","Kirby Club","The Joint Seafood","Always Always","Wakefield Tavern","Mas Salud Kitchen","Bistro d’Azur","Boba Bear","Kushala Sip Coffee House & Tapas Bar ","Ozzy's Apizza","Southern Pines Diner Car","Bold BBQ Pit","Let's Eat","West Tasting Room","Fishbox","Urban Restaurant Group","Throne Brewing","Edoardo's Trattoria","Gastamo Group","Urge + The Barrel Room + Mason Ale Works","Thanks A Brunch","Duke's Ramen","Kim’s Bistro & Bar","FOC Hospitality","Big Jones","Glass Panda","Si Cara","Happy Endings Hospitality","Sticky Rice","The Serving Spoon","The Marshal","Kin","The Art Room","Bocage Champagne Bar","Galit","Urban Decanter","The Local Drive","Lookout Tavern","DNU","Spoon & Pork","TRI","Mandala Kitchen & Bar","Progress Buda","Momoya","Petit Ermitage","Sea Pearl","The Franklin Room","Boni & Mott","Bliss Cafe","Les Trois Chevaux","Figaro Cafe","Goodnight Hospitality","Olmsted","1799 Prime","Feral","Moberi","Chestnut","Good Thanks","Edith’s Pie","The Garret Group","Signature","Russian Samovar","Nola Bar & Kitchen","No More Cafe","Death & Co","Delete","Afterlife Bar","Mockingbird","Golden Hind Wine Bar","Subculture","Byte & Coffee","Harrar Coffee & Roastery","Terasa North Ninth","Mesita","Black Rock Social House","Todd English Hospitality Group","GLUR","Seafood Kingz","Llama Inn","LaLou","1920 Bar and Bistro","Point Seven","Meadowsweet","Sea Salt","Prey Houston","Uplifted Bistro","Commonwealth Joe","Ggiata","Bagel Boss","Bread Bar","inKind Wine Bar","Foxhole","Obet & Del's Coffee Shop","Arboleda Restaurant","Grandpa Hamlet","Super Bien / Buenas","Winston House / The Waterfront","Sticky Fingers Rib House","Nighthawk Brewery & Poppyseed Rye","Go Get Em Tiger","SuperKim Crab House","Jus Grill","Toscana Brick Oven","Cho Dang House","Ms. Cheezious","Proven Poke Co","AMPD Group","Butter Me Up","The Metropolitan","Milo All Day","Raiv Hospitality","Tootles & French","Bosque Brewing Co.","Kalye","Crazy Axes","Hickory Store BBQ","Sonoma Pizza Co.","La Napa","Whaler","Keki Modern Cakes","Mawa's Kitchen","Toki Underground","Sami & Susu","Latin Concepts","Hatch","Redcrest Kitchen","Ritual Social House","La Fendee Mediterranean Grill","Epic Brands","The Post Chicken & Beer","Modern Heirloom","Westover Taco","The Hazel Room PDX","Tavern Companies","Fine Indian Dining Group","Hendrix","Reggae Hut Cafe","Kraken Kourts and Skates","Blue Star Cafe and Pub","Gyro Republic Richmond","Blue Nile","Water Street Grille ","Paradise Street Eats & Biryani","312 Pizza Company","Isaac's Restaurants","Delucca Gaucho Pizza","Cafe Alyce","Doc B's Restaurant","The Ten Bells","Destination Unknown Restaurants","True Food Kitchen","The Cottage","Hen Vietnamese Eatery","Lost Society","Sazoncito Latin Food","Veleros","Soul Bites","Hakuna Hospitality Group","Fish & Rice","Le Madeline","Mr. Tuna","Taqui Taqui","Thunderdome Restaurant Group","JINYA (DMV)","Tiny's & The Bar Upstairs","Altiro Latin Fusion","Sweet Ginger","Miss Delta Southern Restaurant","Lodge Bread","Pow Pow","Kojin 2.0","Taco Guild","The Delta","Kush Hospitality","House of the Rising Buns ","800°","Altamarea Group","Thamee","Employees Only","Boka Restaurant Group ","Carver Road","MaKiin Concepts Hospitality Group","Eno Terra","American Cut Steakhouse","Eating House","Namo","Zitz Sum","Misha's Cupcakes","Saint Bread","Hey Bagel","Distant Worlds Coffeehouse","Bistro, Carvings + Uptowner","Numbers Holding Company ","Proper Orlando","Fashioned Hospitality ","Bluestone Lane","Farra","Botanico Gin and Cookhouse","Lombardis of Sunrise","BunGraze: Flatbread Hamburgers","Tacolicious Dallas","The Coffee Class ","Hook & Line","Veerays ","Palm Beach Meats","Blackthorn Restaurant & Irish Pub","Empanada Loca","Stingray Lounge","The Cave","Walkabout Hospitality Group","Berevino","Libertine","Crudo e Nudo","QP Tapas","ILÉ","Il Totano","Nicolas Eatery","1 Society","63 Degrees Highton","Pilgrim Coffeehouse","Penny Ann's Cafe","Calabash Tea & Tonic","Cafe Cibo Bar","Caffe Dello Sport","Outcast Doughnuts","Max Bar & Grill","Napa Palisades","Unordinary Inc","Julep Bar","Dokkaebier","Goosecup","Collective Coffee Co","CINICO Coffee Company","Gregorys Coffee","Matcha Cita","Dantoni's Pizza","Pachamama and Panela","Kanpai Hospitality","Chicas Tacos","Marmara","Toasty Badger","Ironwood Bar & Grille","Sost","Smokey Bones","The Place 2 Be","5 Acres","Maple & Hash","The Taproom","ViVi Ristorante","Woomiok","Camphor","Nova Espresso","Dayglow","Clipper Coffee","Nicky's Coal Fired Pizza","Santos Kitchen + Lounge","Navy Strength","Tropical Smokehouse","Bridgetown Roti","Casa Thirteen","DELANCEY ST. PIZZA","Habana restaurant ","Bread Winners Cafe & Bakery","Salvation Pizza","Chuck Lager","Frog Club","Amélie","Spicy Moon","Residents","Beerded Goat","Prodigal Son Hospitality","Bloodworth BBQ","Fornino","CoCo B's","Mana Hospitality","Pijja Palace","Corima","Justin Queso's","Poop Deck Bar and Grill","Supreme Thai Bistro","Tavern On The Point","Pelons Tex Mex","Tavern+Bowl East Village","Born & Raised Hospitality","Momentum Coffee","Tasca/Torino","Lazy Point","Unregular Bakery/Pizza","Tara Thai (Montgomery Mall)","Coral Tree Café","Urban Creperie","Di Abruzzo","Hiraya","Stony's Pizza","WAX ON HI","Smoke & Donuts","Tu Madre","Botte","29th Parallel Coffee","Areppas","California Pizza Kitchen","Gyro Republic Sugarland","GoodTimes Brewery","Loyal Legion","Jax Fish House","ReverenceNYC","Mina Group","Dove and Deer","Los Gatos Coffee Co","Comida","Exquisite Creatures","Star Restaurant Group","Guerrilla Tacos","Elementary","The Bantam Kitchen","Mojitos Bistro","Harlem Nights","Lazy Days Brewing","Taylor's Tacos","Cafe Nubia","The Brewer's Table","Big Onion Hospitality","Batter & Berries","City Cellars","Mai Colachi","Little Fatty","Tulum Tacos & Tequila","VHCLE","Hook & Master","The Butcher's Daughter","Bauhaus Biergarten","Tara Kitchen","Bar Louie","Nara Thai","Mi Scuzzi","Loxsmith Bagels","LOL Burger Bar","N17 The Lane","Ludda","Daily Driver","R&R CraftHouse Grill","Jason Emmett's Concepts","Hamburger Mary’s","Beve Cibo","Margot Brooklyn","The Local","Sweet Chick","Berber","The Vig","Bravo Toast","Okan","Charlie Foxtrot Brewing","Driftwood","For the People Hospitality","Chef's Roma Kitchen","Montague Diner","Slim & Husky's","Otto & Pepe","Prezzo","Electrik Karma","Barcade ","Grandma's Home ","Jajaja Group","Thirsty Turtle Seagrill","Phillip Brewery","Yela Concepts","Hospitality Alliance","NADC/Shokunin/Scratch","DCity Smokehouse","Bhuna Restaurant","Maman","Dovetail Pizza","Crossbar","Divino Corp","Ginger Brands","Mama M Sushi","In Good Spirits","El Sol","The Aztec","Cafe Colette","8282","Deep Ellum & Lenora","Crab Pad","Bellota","MOZIAK (Sausage Emporium)","Baxter's R*Cade","Maypole Restaurant","Ms. Icey's Kitchen and Bar","Grata's Pizzeria","Mizza","Colada Shop","Fat Pete's + Cleveland Park Bar & Grill","Vineapple Cafe","Fonda","Rito Loco","Green Almond Pantry","Cilantro Latin Fusion ","Thos. O'Reilly's Public House","Melrose Kitchen","Amelie Wine Bar","Naco Taco & Lily P's","Tacos 2 Go","Dog Daze Social Club","Grand Fir Brewing","Memento Mori Hospitality","Lucky Buns","Union Hospitality Group","Naughty Pie Nature","As You Are","Vine Hospitality","Valley Lodge Restaurant","Blue Plate","Ravish Kitchen","Stem Ciders","Zalat Pizza","Elia Restaurant","Zillions Pizza","Dead Rabbit ","This and That","Kothai Republic","Dotty's Kitchen/Pearl & Lime","The Clubhouse CLT","Doc's Backyard Grill","Tapri Social","Backdeck Bar & Lounge","Southern Gourmet Kitchen","Baan Mae","Tinga Fresh Mexican & BBQ","Parson's","Negroni","Cassava SF","BarTucci / Gino and Marty's","Todos Cantina + Cocina","Budonoki (last day on app 1/17/24)","Bat 17","Pancake Cafe","Pasta Corner","Baba Cool","Bird Dog","The French Crepes","Wilma’s Famous BBQ","L'Experience Paris","The Bronze Owl","Adobo & MoonRise","Zandra's","The Thirsty Clam","Le Mont Royal","Shake It Chicago","Down South CaJJun Eats","Bottleneck Management","KRU","DACHA Kitchen & Bar","JAS & FAM Caribbean Flavor","Ciao Pizzeria Bar","Valedor","Resmex","Not So Bizaare Avenue Cafe","Aviators Wing House","Kazu","Laree Adda","Serafina NYC","TimeOut Bar & Grill","Kraken Axes and Rage","Ten Mile House","Sydney Cebu Lechon","Superiority Burger","Industry","King State","Alliance Hospitality Group","Iron Hill Brewery","Novel Hospitality","Chase's Place Cocktails + Kitchen","The Purple Tongue","Boulevard Hospitality Group","Bamboo House","Dog Haus","Three Points Hospitality","Culture Collective","Krudos Sushi & Modern Kitchen","Lucy's Burger Bar","Blueprints Restaurant Concepts","93 Til Infinity","Eggsperience","Ernesto's","The Paris Cafe","Cape Bottle Room","Saigon Sisters","Little Fish Echo Park","Georgia Brown's","Savta","Fyrebird Chicken","Reggae Jerk Hut","The Little Pig ","Taqueria Picoso","Ditch","Mamaleh's","CoCo Noir Wine Shop","High Cotton Kitchen","1933 Group BA2","Stir House Atlanta","Sushi Ahn","Harold Dean Smoked Goods Smokehouse","Mean Sandwich","RedFarm","Luana's Tavern","Kerbey Lane","Laut","Tuk Tuk Snack Shop","Common Plate Hospitality","Vegan District Asian Eatery","Smögen Appetizers","Mootz Pizzeria and Bar","Lazy Daisy","Old Thousand","Bocadillo Market","San Matteo","Brunchaholics","Odie B's","Hap & Hooch","Avola Kitchen + Bar","DC Taco & Wings","Urban Wine + Kitchen","DMK Restaurant Group","Neighborhood Grills","Johnny Mo's Pizzeria","Calico Fish House","Reunion 19","Rosa Mexicano","Broad Street Oyster Co.","Montclair Hospitality Group","Epic Burger","Horn Barbecue","Lil’ Bowl","Shawn Michelle's Ice Cream","Kae Sushi","Pecado Bueno","Haire's Gulf Shrimp","El Pueblito Taquerias","Crisp Salads NW","Big Bacons","Main Street Emporium","Sheesh","Gertie","La Rue Doughnut","Pokey O's","Valentina's Tex Mex BBQ","Snack Shack 76","BagelWorks Restaurant and Deli","Halalbee's","Dak and Bop","A Timeless Treat","Soul Wingz","Westbound & Down ","Holy Avocado","The Kati Roll Company","East Side King + Thai Kun","Instant Noodle Factory","Holy Que Smokehouse","Mi Ranchito Mexican","Gateway Subs","Winner","Saoco","Ruston Cattle Company","State Park","Choi's","Thai Specialty","Sereneco","Be More Pacific","South Seas","Bareburger","Ketchy Shuby","Peking Duck House","Mah Ze Dahr Bakery","40 North","gtk Hospitality","Bethany Public House","Farow","Farina","S2 Grills","Stout Burgers and Beers","HalfSmoke","Shy Bird","Alidoro","Nostalgic Cafe","Phuc Yea","Smith's American Tavern","Agua 301","Imperial Moto","Mike & Patty's","Aunts et Uncles","Angel's Share Whiskey Lounge and Beer Bar","Protein Bar & Kitchen","Paglia Hospitality","HL Concepts","Burdell","Chef & the Baker","Jerk 48","Tasty Lemon","Vale Food Co","Empanola Mississippi","Happy Chicks","Eat Well Juice Bar","Community Vegan","Wine & Rock Shop","High 5 Entertainment","Tacos Y Mas","Nightlight Donuts","Memphis Seoul","Island Tings","Holy Basil","Thor's Skyr","La Boca Feliz","Nude Pita","Pacific Counter","SUN RICE","Island Provisions ","The Angry Beaver","Press Club","The Concourse Project","Southern Junction","The Red Pavilion","Jean's","Euphoria Hospitality","Otium","Legacy Pie Co","The Grotto","Margot Bar & Bistro","The Bungalow","Criminal Baking Company","Old Tbilisi","Jade Rabbit","Toasted Hospitality","Innovative Dining Group","Lucha Kitchen & Bar","Warsugai","Banh Mi Spot","The Breakfast Klub","Bolay","Divya’s Kitchen","Brazas BBQ Chicken","Reem's","Kapow! Noodle Bar","Empanada Mama","illy","Earl Enterprises","Patti Ann's","Black Rooster Taqueria","Mozwell Claremont","Blackbird Public House","The Monkey King ","Lariele","Wok N' Roll","Operators Club","Pig & Butter","Queenstown Village","Simms Restaurants","Paper Plane Pizza","Alta Adams","The Ainsworth","Exit 12 Mexican Bar & Grill","Ursula","A3 Hospitality","The Kazoku","Capitol Cider House","Immigrant Food","Adrian's Mexican Street Food","Lao'd Bar","Cocina Consuelo","Sweet Patricia's","Spread Kitchen","Volstead ","Sazon De Loa","GASOLINA","Mudbugs","Charlie's Creole Kitchen","Lucille’s","Sumac Mediterranean Cuisine","The Cuban","Lemon Tree Co.","Two Hands","Cross Street Chicken","Irv's Burgers","Beauty's / Cinderella's","Affextionate Cuizine","Wexler's Deli","Conscious Plates","FOMO THG LLC, franchisee of The Halal Guys","Viking Soul Food","Chiddy's Cheesesteaks ","Tokyo Fried Chicken","Effin Egg","Mango Crazy","Novecento","LaSorted’s","Mezeh Mediterranean Grill","Lobstah on a Roll / Gringos","Hot Lola's","Square Roots Hospitality","The Porter House","Le Marais","Moti Modern Indian Kitchen","Kinship Butcher","EuroATL","Right Coast Taqueria","A Street Hospitality","Habana Outpost","Pouring With Heart","Danny Boy's Famous Original Pizza","Lolita's Parlour","Kesos Tacos","Tenseven","Mahana Fresh","Black Seed Bagels + Pebble Bar","Prince St. Pizza","EatYa Pizza ","Hapa Pizza","Forty Deuce","Flavor Hospitality","Planta","The Commons Fooderie","Mezcal Mexican Restaurant","Aslin Beer Company","JINYA Ramen Bar AZ","Super Rad Sub Shop","Blossom's Soul Food","Flagship Restaurant Group","Placebo Restaurant","Amici","Mida","Hue / Rosebar","Tacolicious","Chook Chicken","Millicent Hospitality ","Hangry Bear Creamery","Happy Tuna","Upstream Hospitality","Satellite","Senor Goza","Dreamland","El Centro","Teglia Pizza Bar","Superette","Tulsi Indian Eatery","The Long Goodbye","Ethan Stowell","Juvia Group","Playa Miami","Charisma Workshop","El Raval","Sauf Haus","Coastal","Serpa Hospitality Group","The Ravenous Pig","Broken Compass Tiki","P&M Beverages LLC dba Sandwich Starr","The Bad Apple","Cilantro Taco Grill","JoJo's ShakeBAR","1933 Group TOTP","Acre Restaurant","Chick N Jones","Philly Chop Restaurant & Lounge","Casa Ora","Harolds Chicken Shack","Salt & Time","Tony's Pizza Pasta Grill"]

restaurant_list_json = json.dumps(restaurant_list)
system_prompt = system_prompt_template.format(restaurant_list_json=restaurant_list_json)

# --- Streamlit App ---
st.title("Restaurant Recommendation Chatbot")

# --- Initialize States ---
if 'initialized' not in st.session_state:
    st.session_state['initialized'] = False
if 'chat_started' not in st.session_state:
    st.session_state['chat_started'] = False
if 'location' not in st.session_state:
    st.session_state['location'] = None
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- Automatic Location Detection on First Load ---
if not st.session_state['initialized']:
    st.session_state['initialized'] = True
    st.rerun()  # Forces a rerun on first load to trigger geolocation

# --- Location Handling ---
location = streamlit_geolocation()

col1, col2 = st.columns([3, 1])

with col1:
    if location and isinstance(location, dict) and location.get("latitude") and location.get("longitude"):
        st.session_state['location'] = location
        st.success(f"📍 Location detected: {location['latitude']:.6f}, {location['longitude']:.6f}")
        
        # Optionally, you could display a map here:
        # st.map([{"lat": float(location["latitude"]), "lon": float(location["longitude"])}])
        
        if not st.session_state['chat_started']:
            if st.button("Continue to Chat"):
                st.session_state['chat_started'] = True
                st.rerun()
    else:
        st.warning("📍 Waiting for location access...")
        st.info(
            """Please ensure:
            1. Location permissions are enabled in your browser.
            2. You've accepted the location prompt."""
        )

with col2:
    if st.button("Reset/Restart"):
        # Reset all session state variables
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- Only show chat interface after location is verified and chat is started ---
if st.session_state['location'] and st.session_state['chat_started']:
    # Initialize chat history if empty
    if not st.session_state['history']:
        initial_message = "Hi! I can provide general recommendations or filter by a in-kind partners list if you prefer."
        st.session_state['history'].append({"role": "model", "content": initial_message})
    
    # Display Conversation History
    for turn in st.session_state['history']:
        role = "user" if turn["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(turn["content"])

    # User Input
    user_input = st.chat_input("Enter your message:")

    if user_input:
        # Add user message to history and display it
        st.session_state['history'].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare a placeholder for the assistant's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Searching for restaurants...▌")

        # Build the full prompt from the system prompt, current location, and conversation history
        prompt_parts = [system_prompt]
        # Always update location
        if location and isinstance(location, dict) and location.get("latitude"):
            st.session_state['location'] = location
        
        prompt_parts.append(
            f"User's current location: Latitude {st.session_state['location']['latitude']}, "
            f"Longitude {st.session_state['location']['longitude']}"
        )
        
        # Append conversation history
        for turn in st.session_state['history']:
            prompt_parts.append(f"{turn['role']}: {turn['content']}")
        
        full_prompt = "\n".join(prompt_parts)

        # Generate and stream the response from the model
        full_response = ""
        try:
            # Use a spinner to indicate waiting for the complete response
            with st.spinner("Waiting for response from LLM..."):
                response = model.generate_content(full_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        # Update the message placeholder with the streaming content plus a cursor
                        message_placeholder.markdown(full_response + "▌")
                # Once streaming is complete, update without the cursor
                message_placeholder.markdown(full_response)
        except Exception as e:
            message_placeholder.markdown("Sorry, I encountered an error.")
            st.error(f"An error occurred: {e}")
            full_response = "Error: No response received."

        # Add the final model response to the conversation history
        st.session_state['history'].append({"role": "model", "content": full_response})
elif not st.session_state['location']:
    st.warning("⚠️ Please share your location to start chatting")
elif not st.session_state['chat_started']:
    st.info("Click 'Continue to Chat' to begin the conversation")
