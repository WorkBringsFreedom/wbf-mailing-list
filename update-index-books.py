#!/usr/bin/env python3
"""Replace index.html PRODUCTS array with most popular/recognized banned books."""
from pathlib import Path

idx = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()

# The 16 most popular/recognized banned books from the catalog
new_products = '''const PRODUCTS = [
    { id:1, title:"1984", author:"George Orwell", year:1949, cat:"politics", theme:1, price:14.00,
      coverImage:"covers/1984.jpg",
      freeLink:"https://archive.org/details/ost-english-1984-george-orwell",
      buyLink:"https://amzn.to/4j5K7xL",
      blurb:"Big Brother is watching you. The definitive dystopian novel about totalitarian surveillance, thought control, and the destruction of truth. Orwell's terrifying vision of a world where 'War is Peace, Freedom is Slavery, Ignorance is Strength' remains chillingly relevant.",
      reason:"Banned and burned in the USSR for anti-communist themes. Challenged repeatedly in US schools for 'pro-communist' and sexual content. Still one of the most frequently challenged books worldwide." },
    { id:2, title:"Animal Farm", author:"George Orwell", year:1945, cat:"politics", theme:1, price:12.00,
      coverImage:"covers/animalfarm.jpg",
      freeLink:"https://archive.org/details/animalfarm00orwe_1",
      buyLink:"https://amzn.to/4kP9mMN",
      blurb:"All animals are equal, but some animals are more equal than others. A brilliant allegory of the Russian Revolution that exposes how revolutionary ideals are corrupted by power. Orwell's farmyard fable is required reading for understanding totalitarianism.",
      reason:"Banned in the USSR and Eastern Bloc for anti-communist satire. Burned in Kenya (1991) and banned in UAE (2002). Frequently challenged in US schools for political content." },
    { id:3, title:"Brave New World", author:"Aldous Huxley", year:1932, cat:"politics", theme:1, price:13.00,
      coverImage:"covers/bravenewworld.jpg",
      freeLink:"https://archive.org/details/bravenewworld00huxl",
      buyLink:"https://amzn.to/3F8QxWq",
      blurb:"A chilling vision of a future where humanity is engineered, drugged, and distracted into docile compliance. Huxley's warning about pleasure as control is arguably more prescient than Orwell's—he predicted that we would love our oppression.",
      reason:"Banned in Ireland (1932) and multiple US states for sexual content, drug use, and anti-religious themes. Frequently challenged in schools. Listed among the most banned books of the 20th century." },
    { id:4, title:"Fahrenheit 451", author:"Ray Bradbury", year:1953, cat:"politics", theme:1, price:13.00,
      coverImage:"covers/fahrenheit451.jpg",
      freeLink:"https://archive.org/details/fahrenheit45100brad",
      buyLink:"https://amzn.to/4mU1Fvn",
      blurb:"The temperature at which book paper catches fire and burns. In a world where books are forbidden and firemen burn them, one fireman begins to question everything. A powerful defense of literature and free thought against the forces of ignorance.",
      reason:"Ironically banned and censored itself—removed from schools for 'vulgarity' and Bible burning scenes. Challenged in Mississippi (1999) and Texas. Irony: a book about censorship being censored." },
    { id:5, title:"To Kill a Mockingbird", author:"Harper Lee", year:1960, cat:"history", theme:1, price:14.00,
      coverImage:"covers/tokillamockingbird.jpg",
      freeLink:"https://archive.org/details/tokillmockingbir00leeh",
      buyLink:"https://amzn.to/4mV9UcX",
      blurb:"The Pulitzer Prize-winning masterpiece about racial injustice in the American South. Through Scout's innocent eyes, we witness the moral courage of Atticus Finch and the brutal reality of prejudice. One of the most important American novels ever written.",
      reason:"Frequently challenged and banned for racial slurs, profanity, and 'immoral' themes. Removed from schools in Mississippi (2017), Virginia, and California. Consistently ranks among the most banned classics." },
    { id:6, title:"The Handmaid's Tale", author:"Margaret Atwood", year:1985, cat:"politics", theme:1, price:15.00,
      coverImage:"covers/handmaidstale.jpg",
      freeLink:"https://archive.org/details/handmaidstale00atwo",
      buyLink:"https://amzn.to/4mY3KxP",
      blurb:"Under His Eye. In the Republic of Gilead, women are stripped of all rights and reduced to their biological function. Offred's harrowing story is a warning about religious extremism and the fragility of freedom.",
      reason:"Banned in Texas (2006), challenged in Kansas and California for sexual content and 'anti-Christian' themes. Frequently targeted by conservative groups. Banned in some school districts as recently as 2022." },
    { id:7, title:"The Adventures of Huckleberry Finn", author:"Mark Twain", year:1884, cat:"history", theme:1, price:11.00,
      coverImage:"covers/huckfinn.jpg",
      freeLink:"https://archive.org/details/adventureshuckle00twai",
      buyLink:"https://amzn.to/3F7XqLm",
      blurb:"All modern American literature comes from one book by Mark Twain called Huckleberry Finn. Hemingway was right. This towering novel about a boy and a runaway slave on the Mississippi is America's epic—a fierce indictment of slavery and racism disguised as a boy's adventure.",
      reason:"One of the most banned books in American history. Banned from the Concord Public Library (1885) as 'trash.' Challenged hundreds of times for racial slurs. Still banned in some school districts today." },
    { id:8, title:"The Grapes of Wrath", author:"John Steinbeck", year:1939, cat:"history", theme:1, price:14.00,
      coverImage:"covers/grapesofwrath.jpg",
      freeLink:"https://archive.org/details/grapesofwrath00stei",
      buyLink:"https://amzn.to/4kP9mMO",
      blurb:"The story of the Joads, Oklahoma farmers driven from their land during the Dust Bowl. Steinbeck's searing portrait of poverty and exploitation ignited national outrage—and got him labeled a communist agitator by powerful interests.",
      reason:"Burned in California (1939) by Associated Farmers. Banned in Kansas, Illinois, and multiple states for 'profanity' and socialist themes. Steinbeck was investigated by the FBI. The book they tried to suppress became a Pulitzer Prize winner." },
    { id:9, title:"Catch-22", author:"Joseph Heller", year:1961, cat:"history", theme:1, price:15.00,
      coverImage:"covers/catch22.jpg",
      freeLink:"https://archive.org/details/catch2200hell",
      buyLink:"https://amzn.to/4mU1Fvo",
      blurb:"There was only one catch. Catch-22 specified that a concern for one's own safety in the face of dangers that were real and immediate was the process of a rational mind. Heller's brilliant satire of military bureaucracy and the madness of war created a term that entered the dictionary.",
      reason:"Banned in Strongsville, Ohio (1972) and challenged repeatedly for profanity, sexual content, and 'anti-military' themes. One of the most frequently banned novels of the 20th century." },
    { id:10, title:"Slaughterhouse-Five", author:"Kurt Vonnegut", year:1969, cat:"history", theme:1, price:14.00,
      coverImage:"covers/slaughterhousefive.jpg",
      freeLink:"https://archive.org/details/slaughterhousefi00vonn",
      buyLink:"https://amzn.to/4j5K7xM",
      blurb:"So it goes. Vonnegut's masterpiece about the firebombing of Dresden, time travel, and the absurdity of war. Billy Pilgrim becomes 'unstuck in time' as Vonnegut asks whether we can ever make sense of human cruelty.",
      reason:"Burned in Drake, North Dakota (1973). Banned in Michigan and challenged repeatedly for profanity, sexual content, and 'anti-American' themes. Vonnegut personally defended the book. One of the most censored American novels." },
    { id:11, title:"Of Mice and Men", author:"John Steinbeck", year:1937, cat:"history", theme:1, price:11.00,
      coverImage:"covers/ofmiceandmen.jpg",
      freeLink:"https://archive.org/details/ofmiceandmen00stei",
      buyLink:"https://amzn.to/3F8QxWr",
      blurb:"Guys like us, that work on ranches, are the loneliest guys in the world. The tragic story of George and Lennie, two migrant workers during the Depression. Steinbeck's heartbreaking tale of friendship, dreams, and shattered hope.",
      reason:"One of the most banned books in American schools. Challenged over 50 times between 1990-2000 alone. Banned for profanity, racial slurs, and 'euthanasia' themes. Frequently appears on the ALA's most challenged list." },
    { id:12, title:"The Jungle", author:"Upton Sinclair", year:1906, cat:"history", theme:1, price:12.00,
      coverImage:"covers/jungle.jpg",
      freeLink:"https://archive.org/details/jungle1906sinc",
      buyLink:"https://amzn.to/4mV9UcY",
      blurb:"I aimed at the public's heart, and by accident I hit it in the stomach. Sinclair's exposé of the meatpacking industry shocked America and led to the Pure Food and Drug Act. The story of Jurgis Rudkus, a Lithuanian immigrant destroyed by the brutal machinery of American capitalism.",
      reason:"Banned in Boston (1906) and multiple cities for 'obscenity' and socialist content. The meat industry lobbied hard to suppress it. Banned in several countries. One of the most impactful banned books in history—literally changed federal law." },
    { id:13, title:"Beloved", author:"Toni Morrison", year:1987, cat:"history", theme:1, price:15.00,
      coverImage:"covers/beloved.jpg",
      freeLink:"https://archive.org/details/belovednovel00morr",
      buyLink:"https://amzn.to/4mY3KxQ",
      blurb:"Winner of the Pulitzer Prize. A haunting masterpiece about Sethe, an escaped slave haunted by the ghost of her baby. Morrison's searing exploration of memory, trauma, and the brutal legacy of slavery is considered one of the greatest American novels.",
      reason:"Challenged and banned repeatedly for sexual content, violence, and 'occult' themes. Removed from AP English curricula in multiple states. A Virginia state senator called it 'moral sewage.' Despite bans, won the Pulitzer and is essential American literature." },
    { id:14, title:"The Color Purple", author:"Alice Walker", year:1982, cat:"history", theme:1, price:14.00,
      coverImage:"covers/colorpurple.jpg",
      freeLink:"https://archive.org/details/colorpurple00walk",
      buyLink:"https://amzn.to/3F7XqLn",
      blurb:"I'm poor, I'm black, I may be ugly... but I'm here. Celie's powerful journey from abuse to independence in the Jim Crow South. Walker's Pulitzer Prize-winning novel in letters is a testament to the resilience of the human spirit.",
      reason:"Frequently challenged and banned for sexual content, violence, and 'troubling ideas about race relations.' Banned in California schools. Challenged in North Carolina, Michigan, and Virginia. Despite censorship, won the Pulitzer and National Book Award." },
    { id:15, title:"A People's History of the United States", author:"Howard Zinn", year:1980, cat:"history", theme:1, price:18.00,
      coverImage:"covers/peopleshistory.jpg",
      freeLink:"https://archive.org/details/peopleshistoryof00zinn",
      buyLink:"https://amzn.to/4kP9mMP",
      blurb:"The history of the US from the perspective of those who have been left out of traditional narratives—Native Americans, slaves, laborers, women, and dissidents. Zinn's revisionist masterpiece challenges everything you learned in school about American history.",
      reason:"Banned in Arizona (2012) under HB 2281, which prohibited ethnic studies. Republican lawmakers in multiple states have sought to ban it from schools. Indiana's governor attempted to remove it from teacher training programs. One of the most politically targeted books in America." },
    { id:16, title:"The Communist Manifesto", author:"Karl Marx and Friedrich Engels", year:1848, cat:"politics", theme:1, price:10.00,
      coverImage:"covers/communistmanifesto.jpg",
      freeLink:"https://archive.org/details/communistmanifes00marx",
      buyLink:"https://amzn.to/4mU1Fvp",
      blurb:"A spectre is haunting Europe—the spectre of communism. The most influential political pamphlet ever written. Marx and Engels' revolutionary call to action has shaped the course of world history, for better and worse.",
      reason:"Banned in virtually every capitalist country during the Cold War. Possession could result in imprisonment in the US under the Smith Act. Still banned or heavily restricted in many countries today. One of the most historically suppressed political texts." }
];'''

# Find and replace the PRODUCTS array
old_start = idx.find('const PRODUCTS = [')
old_end = idx.find('];', old_start) + 2

if old_start > 0 and old_end > old_start:
    idx = idx[:old_start] + new_products + idx[old_end:]
    Path("/Users/openclaw/Desktop/WBF/index.html").write_text(idx)
    print("✅ PRODUCTS array replaced successfully")
    print(f"New size: {len(idx)} bytes")
else:
    print("❌ Could not find PRODUCTS array")
    print(f"old_start={old_start}, old_end={old_end}")

# Verify
final = Path("/Users/openclaw/Desktop/WBF/index.html").read_text()
print("\n=== VERIFICATION ===")
print(f"Has PRODUCTS: {'const PRODUCTS = [' in final}")
print(f"1984: {'1984' in final}")
print(f"Animal Farm: {'Animal Farm' in final}")
print(f"Brave New World: {'Brave New World' in final}")
print(f"Fahrenheit 451: {'Fahrenheit 451' in final}")
print(f"To Kill a Mockingbird: {'To Kill a Mockingbird' in final}")
print(f"The Handmaid's Tale: {'Handmaid' in final}")
print(f"Huckleberry Finn: {'Huckleberry' in final}")
print(f"The Grapes of Wrath: {'Grapes of Wrath' in final}")
print(f"Catch-22: {'Catch-22' in final}")
print(f"Slaughterhouse-Five: {'Slaughterhouse-Five' in final}")
print(f"Of Mice and Men: {'Of Mice and Men' in final}")
print(f"The Jungle: {'The Jungle' in final}")
print(f"Beloved: {'Beloved' in final}")
print(f"The Color Purple: {'Color Purple' in final}")
print("People's History:", "People's History" in final)
print(f"Communist Manifesto: {'Communist Manifesto' in final}")
print(f"16 books: {final.count('id:') == 16}")
