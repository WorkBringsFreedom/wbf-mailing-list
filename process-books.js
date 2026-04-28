const fs = require('fs');
const path = require('path');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function slugify(title) {
  return title.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-+/g, '-');
}

async function fetchGB(title, author) {
  const q = encodeURIComponent(`intitle:${title} inauthor:${author}`);
  try {
    const res = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${q}&maxResults=1`, { timeout: 10000 });
    const data = await res.json();
    if (data.items && data.items[0] && data.items[0].volumeInfo && data.items[0].volumeInfo.industryIdentifiers) {
      for (const id of data.items[0].volumeInfo.industryIdentifiers) {
        if (id.type === 'ISBN_13') return id.identifier;
        if (id.type === 'ISBN_10') return id.identifier;
      }
    }
  } catch (e) { console.log('  GB error:', e.message); }
  return null;
}

async function fetchArchive(title, author) {
  const q = encodeURIComponent(`title:${title} creator:${author}`);
  try {
    const res = await fetch(`https://archive.org/advancedsearch.php?q=${q}&fl[]=identifier&sort[]=downloads+desc&rows=1&output=json`, { timeout: 10000 });
    const data = await res.json();
    if (data.response && data.response.docs && data.response.docs[0]) {
      return `https://archive.org/details/${data.response.docs[0].identifier}`;
    }
  } catch (e) { console.log('  IA error:', e.message); }
  return null;
}

async function downloadCover(isbn, filepath) {
  try {
    const res = await fetch(`https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`, { timeout: 15000 });
    if (res.ok) {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('image')) {
        const buf = Buffer.from(await res.arrayBuffer());
        if (buf.length > 1000) {
          fs.writeFileSync(filepath, buf);
          return true;
        }
      }
    }
  } catch (e) {}
  return false;
}

function mapCat(raw) {
  const r = raw.toLowerCase();
  if (r.includes('politics') || r.includes('political')) return 'politics';
  if (r.includes('philosophy')) return 'philosophy';
  if (r.includes('history')) return 'history';
  if (r.includes('sociology')) return 'sociology';
  if (r.includes('censorship')) return 'politics';
  if (r.includes('strategy')) return 'politics';
  if (r.includes('economics')) return 'politics';
  if (r.includes('religion')) return 'philosophy';
  return 'politics';
}

// All 100 books from banned2.pdf
// [pdf_num, title, author, year, rawCategory, price, blurb, reason]
const books = [
  [1,"1984","George Orwell",1949,"Politics",16,"In a totalitarian superstate, Winston Smith dares to think for himself. Orwell's chilling prophecy of surveillance, propaganda, and the destruction of truth.","Totalitarianism · Surveillance · Thoughtcrime · Censorship"],
  [2,"Animal Farm","George Orwell",1945,"Politics",16,"All animals are equal, but some animals are more equal than others. A savage allegory of revolution betrayed by power-hungry elites.","Allegory · Revolution · Soviet Union · Power"],
  [3,"The Communist Manifesto","Karl Marx and Friedrich Engels",1848,"Politics / Philosophy",14,"The most influential political pamphlet ever written. Marx and Engels' call to workers of the world to unite against capitalist exploitation.","Class warfare · Revolution · Capitalism critique · Banned in multiple regimes"],
  [4,"Das Kapital","Karl Marx",1867,"Politics / Economics",18,"The foundational critique of political economy. Marx's analysis of labor, surplus value, and the contradictions inherent in capitalism.","Economics · Labor theory · Anti-capitalism · Censorship"],
  [5,"The Road to Serfdom","Friedrich Hayek",1944,"Political Philosophy",16,"Hayek's warning that centralized economic planning inevitably leads to totalitarianism. A libertarian classic that reshaped post-war political thought.","Libertarianism · Central planning · Totalitarianism · Free markets"],
  [6,"The Rights of Man","Thomas Paine",1791,"Politics",14,"Paine's passionate defense of the French Revolution and universal human rights against Edmund Burke's conservatism. A rallying cry for democracy.","Human rights · French Revolution · Republicanism · Radicalism"],
  [7,"Common Sense","Thomas Paine",1776,"Politics",14,"The pamphlet that convinced America to declare independence. Paine's plain-spoken argument for republican government over monarchy.","American Revolution · Independence · Republicanism · Monarchy"],
  [8,"The Social Contract","Jean-Jacques Rousseau",1762,"Political Philosophy",14,"Man is born free, yet everywhere he is in chains. Rousseau's theory of legitimate political authority based on the general will.","Popular sovereignty · General will · Freedom · Political legitimacy"],
  [9,"On Liberty","John Stuart Mill",1859,"Political Philosophy",14,"The classic defense of individual freedom against state and social coercion. Mill's harm principle remains the bedrock of liberal thought.","Individual freedom · Harm principle · Free speech · Liberalism"],
  [10,"Leviathan","Thomas Hobbes",1651,"Political Philosophy",14,"Life in the state of nature is solitary, poor, nasty, brutish, and short. Hobbes' argument for absolute sovereignty to escape the war of all against all.","Social contract · Sovereignty · Human nature · Authority"],
  [11,"The Prince","Niccolo Machiavelli",1532,"Political Philosophy",14,"The ends justify the means. Machiavelli's ruthless manual for acquiring and maintaining political power scandalized Europe for centuries.","Realpolitik · Power · Statecraft · Amorality"],
  [12,"Discourses on Livy","Niccolo Machiavelli",1531,"Political Philosophy / History",14,"Machiavelli's deeper reflection on republican government, civic virtue, and the maintenance of free states through citizen participation.","Republicanism · Civic virtue · Roman history · Liberty"],
  [13,"Two Treatises of Government","John Locke",1689,"Political Philosophy",14,"Locke's revolutionary argument for natural rights, government by consent, and the right to revolution. The philosophical foundation of modern democracy.","Natural rights · Social contract · Consent · Revolution"],
  [14,"Democracy in America","Alexis de Tocqueville",1835,"Politics / Sociology",16,"Tocqueville's prophetic analysis of the American experiment — its strengths, its dangers, and its inevitable slide toward soft despotism.","American democracy · Equality · Despotism · Civil society"],
  [15,"Reflections on the Revolution in France","Edmund Burke",1790,"Politics",14,"The foundational conservative text. Burke's warning against radical revolution, abstract rights, and the destruction of inherited institutions and tradition.","Conservatism · Tradition · Anti-revolution · Natural order"],
  [16,"The Federalist Papers","Alexander Hamilton, James Madison, John Jay",1788,"Politics",16,"The original defense of the U.S. Constitution. Hamilton, Madison, and Jay's essays remain the essential text for understanding the Founders' vision.","Founding · Constitution · Republic · Separation of powers"],
  [17,"The State and Revolution","Vladimir Lenin",1917,"Politics",16,"Lenin's blueprint for smashing the bourgeois state and establishing the dictatorship of the proletariat. The revolutionary handbook that changed history.","Revolution · Proletariat · Dictatorship · Marxism"],
  [18,"What Is to Be Done?","Vladimir Lenin",1902,"Politics",16,"Lenin's call for a vanguard party to lead the working class to revolution. The theoretical foundation of Bolshevik organization.","Vanguard party · Class consciousness · Organization · Revolution"],
  [19,"Quotations from Chairman Mao Tse-tung","Mao Zedong",1964,"Politics",16,"The Little Red Book that became the bible of the Cultural Revolution. Mao's aphorisms on revolution, class struggle, and perpetual warfare.","Cultural Revolution · Class struggle · Propaganda · Totalitarianism"],
  [20,"The Wretched of the Earth","Frantz Fanon",1961,"Politics / Sociology",16,"The definitive text on anti-colonial struggle and the psychology of decolonization. Fanon's passionate call for violent liberation from imperial rule.","Anti-colonialism · Decolonization · Violence · Liberation"],
  [21,"Black Skin, White Masks","Frantz Fanon",1952,"Sociology / Philosophy",16,"Fanon's searing analysis of the psychological damage inflicted by racism and colonial domination. A foundational text of postcolonial theory.","Racism · Colonialism · Identity · Psychology"],
  [22,"Pedagogy of the Oppressed","Paulo Freire",1968,"Politics / Sociology",16,"Education as a practice of freedom. Freire's revolutionary method for teaching critical consciousness to the poor and marginalized.","Education · Critical consciousness · Liberation · Marginalization"],
  [23,"The Open Veins of Latin America","Eduardo Galeano",1971,"History / Politics",16,"Five centuries of the plunder of a continent. Galeano's passionate indictment of colonialism, imperialism, and the extraction of Latin American wealth.","Imperialism · Colonialism · Economic exploitation · Latin America"],
  [24,"How to Read Donald Duck","Ariel Dorfman and Armand Mattelart",1971,"Politics / Sociology",16,"Dorfman and Mattelart expose the imperialist ideology hidden in Disney comics. A classic of cultural criticism from Pinochet's Chile.","Cultural imperialism · Media criticism · Disney · Ideology"],
  [25,"The Gulag Archipelago","Aleksandr Solzhenitsyn",1973,"History / Politics",18,"Solzhenitsyn's monumental expose of the Soviet forced labor camp system. The book that helped dismantle the moral credibility of communism.","Soviet Union · Labor camps · Totalitarianism · Dissent"],
  [26,"One Day in the Life of Ivan Denisovich","Aleksandr Solzhenitsyn",1962,"History / Politics",16,"A single day in a Soviet labor camp, told with devastating simplicity. The first major literary work to break the silence on the Gulag.","Gulag · Soviet repression · Survival · Dissent"],
  [27,"Doctor Zhivago","Boris Pasternak",1957,"History / Politics",16,"A love story set against the Russian Revolution and Civil War. Pasternak's novel was banned in the USSR and smuggled to the West for publication.","Russian Revolution · Censorship · Romance · Dissident literature"],
  [28,"Homage to Catalonia","George Orwell",1938,"History / Politics",16,"Orwell's firsthand account of fighting fascism in the Spanish Civil War. A masterpiece of war reportage and a warning about Soviet propaganda.","Spanish Civil War · Fascism · Soviet interference · Journalism"],
  [29,"The Origins of Totalitarianism","Hannah Arendt",1951,"Politics / History",18,"Arendt's magisterial analysis of how totalitarian regimes arise from the collapse of class society. Essential reading for understanding modern tyranny.","Totalitarianism · Nazism · Stalinism · Political theory"],
  [30,"Eichmann in Jerusalem","Hannah Arendt",1963,"History / Philosophy",16,"Arendt's controversial report on the banality of evil. Her analysis of Adolf Eichmann's trial challenged how we understand responsibility for atrocity.","Holocaust · Evil · Responsibility · Controversy"],
  [31,"The Human Condition","Hannah Arendt",1958,"Philosophy / Politics",16,"Arendt's philosophical exploration of labor, work, and action in the vita activa. A profound meditation on what it means to live a genuinely political life.","Political philosophy · Action · Labor · Modernity"],
  [32,"Discipline and Punish","Michel Foucault",1975,"Philosophy / Sociology",16,"Foucault traces the transformation from public execution to the modern prison, revealing how power operates through surveillance and normalization.","Surveillance · Prison · Power · Social control"],
  [33,"The History of Sexuality","Michel Foucault",1976,"Sociology / Philosophy",16,"Sexuality is not a natural given but a construct of power. Foucault's radical rethinking of how societies regulate bodies and desires.","Sexuality · Power · Social construction · Repression"],
  [34,"Madness and Civilization","Michel Foucault",1961,"Philosophy / History",16,"Foucault's history of how Western society confined and medicalized madness, transforming the madman from a vessel of truth into a pathological case.","Madness · Psychiatry · Power · Social exclusion"],
  [35,"The Second Sex","Simone de Beauvoir",1949,"Philosophy / Sociology",16,"One is not born, but rather becomes, a woman. Beauvoir's existentialist analysis of women's oppression remains the cornerstone of feminist philosophy.","Feminism · Existentialism · Gender · Oppression"],
  [36,"The Ethics of Ambiguity","Simone de Beauvoir",1947,"Philosophy",16,"Beauvoir applies existentialism to ethics, arguing that freedom demands action and that we are responsible for creating meaning in an ambiguous world.","Existentialism · Ethics · Freedom · Responsibility"],
  [37,"Being and Nothingness","Jean-Paul Sartre",1943,"Philosophy",18,"Sartre's monumental treatise on existential phenomenology. We are condemned to be free, and existence precedes essence.","Existentialism · Freedom · Consciousness · Phenomenology"],
  [38,"Nausea","Jean-Paul Sartre",1938,"Philosophy",16,"Roquentin's existential crisis in a provincial town reveals the contingency and absurdity of existence. Sartre's first novel and existentialist manifesto.","Existentialism · Absurdity · Contingency · Alienation"],
  [39,"The Myth of Sisyphus","Albert Camus",1942,"Philosophy",16,"There is but one truly serious philosophical problem, and that is suicide. Camus' essay on absurdity and the revolt that gives life meaning.","Absurdism · Suicide · Meaning · Revolt"],
  [40,"The Rebel","Albert Camus",1951,"Philosophy / Politics",16,"Camus examines revolution and rebellion from the French Revolution to the Soviet era, arguing that murder in the name of utopia destroys humanity.","Rebellion · Revolution · Violence · Humanism"],
  [41,"Thus Spoke Zarathustra","Friedrich Nietzsche",1883,"Philosophy",14,"Nietzsche's philosophical novel announces the death of God and the coming of the Ubermensch. A prophetic, poetic masterpiece of modern thought.","Nihilism · Ubermensch · Will to power · Prophecy"],
  [42,"Beyond Good and Evil","Friedrich Nietzsche",1886,"Philosophy",14,"Nietzsche demolishes traditional morality and calls for a revaluation of all values. A devastating critique of religion, philosophy, and democracy.","Morality · Religion · Democracy critique · Revaluation"],
  [43,"The Genealogy of Morals","Friedrich Nietzsche",1887,"Philosophy",14,"Nietzsche traces the origins of guilt, conscience, and ascetic ideals to resentment and the will to power. A psychological masterwork.","Morality · Resentment · Guilt · Psychology"],
  [44,"The Will to Power","Friedrich Nietzsche",1901,"Philosophy",14,"A posthumous collection of Nietzsche's notes on nihilism, power, and the transvaluation of values. Controversial but indispensable for understanding his thought.","Nihilism · Power · Transvaluation · Posthumous"],
  [45,"Critique of Pure Reason","Immanuel Kant",1781,"Philosophy",14,"Kant's revolutionary investigation into the limits of human knowledge. We can only know phenomena, not things-in-themselves.","Epistemology · Reason · Phenomena · Limits of knowledge"],
  [46,"Religion within the Bounds of Bare Reason","Immanuel Kant",1793,"Philosophy",14,"Kant argues that moral religion requires no revelation, only reason. A radical rethinking of faith that scandalized theologians and censors alike.","Religion · Morality · Reason · Enlightenment"],
  [47,"The Republic","Plato",-375,"Political Philosophy",14,"Plato's vision of the just city ruled by philosopher-kings. The foundational text of Western political philosophy and the theory of ideal forms.","Justice · Philosopher-king · Ideal forms · Utopia"],
  [48,"Politics","Aristotle",-350,"Political Philosophy",14,"The original political science. Aristotle's systematic analysis of constitutions, citizenship, virtue, and the good life — the foundation of Western political thought.","Classical philosophy · Virtue · Citizenship · Natural law"],
  [49,"The Art of War","Sun Tzu",-500,"Politics / Strategy",14,"The ancient Chinese treatise on strategy, deception, and victory without battle. Still studied in military academies and boardrooms worldwide.","Strategy · Warfare · Deception · Leadership"],
  [50,"The Trial","Franz Kafka",1925,"Politics / Philosophy",16,"Joseph K. is arrested and executed without ever learning his crime. Kafka's nightmare vision of modern bureaucracy and incomprehensible justice.","Bureaucracy · Absurdism · Guilt · Totalitarianism"],
  [51,"Brave New World","Aldous Huxley",1932,"Politics / Philosophy",16,"A future of genetic engineering, soma, and manufactured happiness. Huxley's dystopia warns that pleasure, not pain, may be the ultimate instrument of control.","Dystopia · Genetic engineering · Hedonism · Control"],
  [52,"Fahrenheit 451","Ray Bradbury",1953,"Politics / Censorship",16,"Firemen burn books in a society where critical thought is criminal. Bradbury's warning about censorship, entertainment, and the death of curiosity.","Censorship · Book burning · Anti-intellectualism · Conformity"],
  [53,"A Clockwork Orange","Anthony Burgess",1962,"Politics / Sociology",16,"Ultraviolence and state-sponsored mind control collide in Burgess' disturbing fable of free will. Can goodness be mechanically imposed?","Free will · Violence · Behaviorism · Morality"],
  [54,"We","Yevgeny Zamyatin",1924,"Politics",16,"The original dystopian novel that inspired 1984 and Brave New World. Zamyatin's We envisioned total surveillance and the destruction of the individual.","Dystopia · Surveillance · Individuality · Totalitarianism"],
  [55,"Darkness at Noon","Arthur Koestler",1940,"Politics",16,"A former Bolshevik is forced to confess to imaginary crimes in Stalin's show trials. Koestler's devastating portrait of ideological self-destruction.","Stalinism · Show trials · Confession · Ideology"],
  [56,"The Handmaid's Tale","Margaret Atwood",1985,"Politics / Sociology",16,"A theocratic regime reduces women to breeders in a dystopian America. Atwood's chilling warning about religious fundamentalism and patriarchal control.","Theocracy · Patriarchy · Reproductive rights · Dystopia"],
  [57,"The Grapes of Wrath","John Steinbeck",1939,"History / Sociology",16,"Dust Bowl farmers are driven from their land and crushed by economic forces beyond their control. Steinbeck's epic of dignity amid American poverty.","Great Depression · Poverty · Migration · Labor"],
  [58,"Of Mice and Men","John Steinbeck",1937,"Sociology",16,"Two migrant workers dream of owning land in a world that crushes the weak. Steinbeck's tragedy of friendship, loneliness, and the American Dream.","Poverty · Friendship · American Dream · Disability"],
  [59,"To Kill a Mockingbird","Harper Lee",1960,"History / Sociology",16,"Atticus Finch defends a Black man falsely accused of rape in the Jim Crow South. A timeless examination of racism, courage, and moral conscience.","Racism · Jim Crow · Justice · Courage"],
  [60,"The Adventures of Huckleberry Finn","Mark Twain",1884,"History / Sociology",14,"Huck and Jim's river journey exposes the cruelty and absurdity of antebellum America. The most banned American classic for its language and truth.","Slavery · Racism · Adventure · Controversy"],
  [61,"Native Son","Richard Wright",1940,"Sociology / Politics",16,"Bigger Thomas' violence forces America to confront systemic racism. Wright's unflinching naturalist novel shattered the liberal consensus on race.","Racism · Violence · Systemic oppression · Naturalism"],
  [62,"Black Boy","Richard Wright",1945,"History / Sociology",16,"Wright's autobiography of growing up Black in the Jim Crow South. A searing account of hunger, violence, and the struggle for intellectual freedom.","Autobiography · Jim Crow · Hunger · Intellectual freedom"],
  [63,"Invisible Man","Ralph Ellison",1952,"Sociology / Politics",16,"A nameless Black man navigates a society that refuses to see him. Ellison's masterpiece of identity, visibility, and the American racial nightmare.","Identity · Racism · Invisibility · American Dream"],
  [64,"Go Tell It on the Mountain","James Baldwin",1953,"Sociology",16,"A Harlem teenager confronts religion, family, and sexuality on his fourteenth birthday. Baldwin's semi-autobiographical debut of spiritual crisis.","Religion · Sexuality · Harlem · Coming of age"],
  [65,"The Fire Next Time","James Baldwin",1963,"Politics / Sociology",16,"Baldwin's urgent letters on race in America. If we do not dare everything, the fulfillment of that prophecy, re-created from the Bible in song by a slave, is upon us.","Race · Religion · Civil rights · Prophecy"],
  [66,"I Know Why the Caged Bird Sings","Maya Angelou",1969,"History / Sociology",16,"Angelou's autobiography of trauma, racism, and finding her voice in the segregated South. A testament to the resilience of the human spirit.","Autobiography · Trauma · Racism · Resilience"],
  [67,"The Autobiography of Malcolm X","Malcolm X and Alex Haley",1965,"History / Politics",16,"From street hustler to revolutionary icon, Malcolm X tells his story with unflinching honesty. One of the most influential American autobiographies ever written.","Autobiography · Black nationalism · Islam · Transformation"],
  [68,"Soul on Ice","Eldridge Cleaver",1968,"Politics / Sociology",16,"Cleaver's essays from Folsom Prison electrified the Black Power movement. Controversial, provocative, and essential to understanding 1960s radicalism.","Black Power · Prison · Revolution · Controversy"],
  [69,"Assata: An Autobiography","Assata Shakur",1987,"Politics / History",16,"Shakur's account of her life, trial, and escape from prison. A powerful document of Black liberation and state repression in America.","Black Liberation · Prison · Police · State repression"],
  [70,"The New Jim Crow","Michelle Alexander",2010,"Sociology / Politics",16,"Mass incarceration has replaced segregation as the primary tool of racial control. Alexander's devastating legal and historical analysis.","Mass incarceration · Racism · Criminal justice · Systemic oppression"],
  [71,"Stamped from the Beginning","Ibram X. Kendi",2016,"History / Sociology",16,"Kendi traces the history of racist ideas from Puritan America to the present. A comprehensive account of how anti-Black thought was constructed and defended.","Racism · Intellectual history · Anti-Blackness · Construction"],
  [72,"How to Be an Antiracist","Ibram X. Kendi",2019,"Sociology / Politics",16,"Kendi argues that neutrality is impossible in a racist society. A memoir and manifesto for actively dismantling racist policies and ideas.","Antiracism · Policy · Neutrality · Activism"],
  [73,"White Fragility","Robin DiAngelo",2018,"Sociology",16,"DiAngelo examines why white Americans struggle to talk about racism. A provocative analysis of defensive reactions to racial inequality.","Whiteness · Defensiveness · Racial inequality · Privilege"],
  [74,"Between the World and Me","Ta-Nehisi Coates",2015,"Sociology / Politics",16,"Coates' letter to his son about being Black in America. A searing meditation on the body, fear, and the American dream's betrayal.","Black body · Fear · Fatherhood · American Dream"],
  [75,"A People's History of the United States","Howard Zinn",1980,"History / Politics",16,"History from the perspective of workers, women, slaves, and indigenous people. Zinn's revisionist classic challenges every heroic national myth.","Revisionism · Class struggle · Indigenous · Labor"],
  [76,"Lies My Teacher Told Me","James W. Loewen",1995,"History",16,"Loewen reveals the omissions, distortions, and false hero worship in American history textbooks. Essential reading for historical literacy.","Textbooks · Historical distortion · Mythology · Education"],
  [77,"Bury My Heart at Wounded Knee","Dee Brown",1970,"History / Politics",16,"The systematic destruction of Native American tribes from 1860 to 1890, told from indigenous perspectives. A heartbreaking chronicle of genocide.","Native American · Genocide · Westward expansion · Broken treaties"],
  [78,"An Indigenous Peoples' History of the United States","Roxanne Dunbar-Ortiz",2014,"History / Politics",16,"Dunbar-Ortiz reframes American history as a centuries-long project of indigenous dispossession. A necessary corrective to settler colonial narratives.","Indigenous · Settler colonialism · Dispossession · Resistance"],
  [79,"1491","Charles C. Mann",2005,"History",16,"The Americas before Columbus were far more populous and sophisticated than we were taught. Mann demolishes the myth of pristine wilderness.","Pre-Columbian · Indigenous · Demographics · Revisionism"],
  [80,"1493","Charles C. Mann",2011,"History",16,"The Columbian Exchange created a new world of trade, disease, and ecological transformation. Mann traces the global consequences of 1492.","Columbian Exchange · Globalization · Ecology · Trade"],
  [81,"The Diary of a Young Girl","Anne Frank",1947,"History",16,"A Jewish girl hides from the Nazis in an Amsterdam attic, recording her hopes, fears, and growing up in confinement. Humanity's most read Holocaust document.","Holocaust · Jewish · Diary · Innocence"],
  [82,"Night","Elie Wiesel",1960,"History",16,"Wiesel's memoir of surviving Auschwitz and Buchenwald. A devastating testimony to the death of God, the death of innocence, and the death of humanity.","Holocaust · Auschwitz · Faith · Testimony"],
  [83,"Maus","Art Spiegelman",1980,"History",16,"Nazis are cats, Jews are mice in this Pulitzer-winning graphic novel. Spiegelman's father's survival story becomes a meditation on trauma and memory.","Holocaust · Graphic novel · Trauma · Memory"],
  [84,"Persepolis","Marjane Satrapi",2000,"History / Politics",16,"A young girl comes of age during the Iranian Revolution and Iran-Iraq War. Satrapi's graphic memoir captures the absurdity and tragedy of living under fundamentalism.","Iranian Revolution · Graphic memoir · Fundamentalism · Childhood"],
  [85,"The Things They Carried","Tim O'Brien",1990,"History / Politics",16,"A metafictional masterpiece about the Vietnam War and the stories soldiers tell to survive. Blurring truth and fiction, O'Brien captures war's moral ambiguity.","Vietnam War · Fiction · Truth · Memory"],
  [86,"Catch-22","Joseph Heller",1961,"Politics / History",16,"A bombardier tries to prove he is insane to avoid flying more missions, but only a sane man would want to stop. Heller's absurdist war satire.","War · Bureaucracy · Absurdism · Satire"],
  [87,"Slaughterhouse-Five","Kurt Vonnegut",1969,"History / Politics",16,"Billy Pilgrim becomes unstuck in time after surviving the firebombing of Dresden. Vonnegut's anti-war classic fuses sci-fi with the trauma of total war.","Dresden · Time travel · Anti-war · Trauma"],
  [88,"Johnny Got His Gun","Dalton Trumbo",1939,"Politics / History",16,"A soldier loses his limbs, face, and senses but remains conscious. Trumbo's nightmarish anti-war novel was blacklisted during the McCarthy era.","Anti-war · Disability · Consciousness · Blacklist"],
  [89,"All Quiet on the Western Front","Erich Maria Remarque",1929,"History / Politics",16,"A German soldier loses his innocence and his generation in the trenches of World War I. Remarque's unflinching classic was banned and burned by the Nazis.","World War I · Trench warfare · Loss of innocence · Nazi book burning"],
  [90,"The Jungle","Upton Sinclair",1906,"Politics / Sociology",16,"Lithuanian immigrants are ground up by Chicago's meatpacking industry. Sinclair aimed for America's heart and hit its stomach, sparking food safety reform.","Labor · Immigration · Meatpacking · Muckraking"],
  [91,"Nickel and Dimed","Barbara Ehrenreich",2001,"Sociology / Politics",16,"A journalist goes undercover in minimum-wage America and discovers that hard work does not pay the rent. A damning indictment of the working poor.","Poverty · Minimum wage · Working poor · Inequality"],
  [92,"Evicted","Matthew Desmond",2016,"Sociology",16,"Desmond follows eight families in Milwaukee as they struggle to keep a roof over their heads. A landmark work on housing, poverty, and exploitation.","Housing · Eviction · Poverty · Inequality"],
  [93,"The Color Purple","Alice Walker",1982,"Sociology / History",16,"Celie finds her voice and her freedom through sisterhood and self-love in the Jim Crow South. Walker's Pulitzer-winning epistolary novel.","Racism · Sexism · Sisterhood · Self-discovery"],
  [94,"Beloved","Toni Morrison",1987,"History / Sociology",16,"A former slave is haunted by the child she killed to spare from slavery. Morrison's Pulitzer masterpiece probes the unspeakable trauma of American bondage.","Slavery · Trauma · Haunting · Memory"],
  [95,"The Bluest Eye","Toni Morrison",1970,"Sociology",16,"A Black girl prays for blue eyes, believing beauty will bring love. Morrison's devastating debut exposes how white supremacy destroys Black self-worth.","Beauty standards · Internalized racism · Childhood · Trauma"],
  [96,"Song of Solomon","Toni Morrison",1977,"Sociology / History",16,"Milkman Dead's quest for his ancestral past becomes a mythic journey through Black American history. Morrison's soaring novel of flight, freedom, and legacy.","Black identity · Ancestry · Flight · Myth"],
  [97,"Things Fall Apart","Chinua Achebe",1958,"History / Sociology",16,"Okonkwo's tragic decline mirrors the destruction of Igbo society by British colonialism. Achebe's masterpiece gave Africa its voice in world literature.","Colonialism · Igbo · Tradition · Tragedy"],
  [98,"The Satanic Verses","Salman Rushdie",1988,"Politics / Religion / Censorship",18,"A fatwa was issued for this novel's alleged blasphemy. Rushdie's magical realist epic about migration, identity, and the nature of revelation.","Blasphemy · Fatwa · Migration · Magical realism"],
  [99,"The Bible","Various",-100,"Philosophy / History",14,"The foundational text of Western civilization, banned and burned across millennia by regimes seeking to control sacred access to divine truth.","Religion · Authority · Censorship · Scripture"],
  [100,"The Qur'an","Various",650,"Philosophy / History",14,"The holy book of Islam, banned and restricted by colonial and secular authorities who feared its power to mobilize resistance and shape civilization.","Islam · Revelation · Colonialism · Scripture"],
];

async function main() {
  const coversDir = path.join(__dirname, 'covers');
  if (!fs.existsSync(coversDir)) fs.mkdirSync(coversDir, {recursive:true});

  const enriched = [];
  let coversFound = 0;
  let archivesFound = 0;
  const needsAttention = [];

  for (let i = 0; i < books.length; i++) {
    const [pdfNum, title, author, year, rawCat, price, blurb, reason] = books[i];
    const id = 16 + pdfNum; // IDs 17-116
    console.log(`Processing ${id}: ${title}`);
    const slug = slugify(title);
    const coverPath = path.join(coversDir, `${slug}.jpg`);
    const relativeCover = `covers/${slug}.jpg`;

    let coverImage = null;
    let freeLink = null;

    const isbn = await fetchGB(title, author);
    if (isbn) {
      const ok = await downloadCover(isbn, coverPath);
      if (ok) {
        coverImage = relativeCover;
        coversFound++;
        console.log(`  Cover: ${isbn}`);
      } else {
        console.log(`  Cover download failed for ISBN ${isbn}`);
      }
    } else {
      console.log(`  No ISBN found`);
    }

    freeLink = await fetchArchive(title, author);
    if (freeLink) {
      archivesFound++;
      console.log(`  Archive: ${freeLink}`);
    } else {
      console.log(`  No archive link`);
    }

    if (!coverImage && !freeLink) {
      needsAttention.push({id, title, author});
    }

    const buyLink = `https://www.amazon.com/s?k=${encodeURIComponent(title + ' ' + author)}`;

    enriched.push({
      id, title, author, year, cat: mapCat(rawCat), price, coverImage, freeLink, buyLink, blurb, reason
    });

    await sleep(300);
  }

  fs.writeFileSync(path.join(__dirname, 'books-100.json'), JSON.stringify(enriched, null, 2));
  console.log(`\n=== DONE ===`);
  console.log(`Total books: ${enriched.length}`);
  console.log(`Covers found: ${coversFound}/${books.length}`);
  console.log(`Archive links found: ${archivesFound}/${books.length}`);
  console.log(`Needs attention (${needsAttention.length}):`);
  for (const b of needsAttention) console.log(`  - ${b.title} by ${b.author}`);
}

main().catch(e => { console.error(e); process.exit(1); });
