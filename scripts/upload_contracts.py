import sqlite3
import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DB_PATH = os.path.join(project_root, "hh_stats.db")

TEAMS = [
    'Boston Celtics', 'Brooklyn Nets', 'Montreal Mastodons', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors',
    'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers', 'Milwaukee Bucks',
    'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat', 'Orlando Magic', 'Washington Wizards',
    'Denver Nuggets', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Portland Trailblazers', 'Utah Jazz',
    'Golden State Warriors', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings',
    'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans',
    'San Antonio Spurs', 'San Diego Caravels'
]

IGNORE_KEYWORDS = ["TOTALS", "SALARY CAP", "HARD CAP"]

PLAYER_NAME_MAP = {
    "Kelly Oubre Jr": "Kelly Oubre",
    "Jabari Smith Jr": "Jabari Smith",
    "Bruce Brown Jr": "Bruce Brown",
    "Ronald Holland II": "Ron Holland", 
    "Wendell Carter Jr": "Wendell Carter",
    "Jaime Jaquez Jr": "Jaime Jaquez",
    "Nicolas Claxton": "Nic Claxton",
    "Herbert Jones": "Herb Jones", 
    "Cam Reddish": "Cameron Reddish",
    "Kevin Porter Jr": "Kevin Porter",
    "Nick Smith Jr": "Nick Smith",
    "Vince Williams Jr": "Vince Williams",
    "Dereck Lively II": "Dereck Lively",
    "Trey Murphy III": "Trey Murphy"
}

RAW_DATA = """✉		Atlanta Hawks					
81	*	Jalen Green	$38,661,750	$41,561,381	$44,461,013	$47,360,644	
79	*	DeAndre Hunter	$23,303,571	$24,910,714			
78	*	Jabari Smith Jr	$12,350,392	$16,203,715			
78	*	Bennedict Mathurin	$9,187,573	$12,256,222			
78	*	Russell Westbrook	$9,000,000	$9,000,000	$9,000,000		
78	*	Jalen Suggs	$38,661,750	$41,561,381	$44,461,013	$47,360,644	
77	*	Nic Claxton	$37,783,025	$40,419,050	$43,055,075	$45,691,100	
75	*	Isaiah Jackson	$18,000,000	$16,727,130			
73	*	Kevin Porter Jr	$5,284,305	$4,011,435	$2,738,565	$1,465,695	
72	*	Marcus Sasser	$2,886,431	$5,198,462	$8,156,386		
72	*	Kyle Filipowski	$3,353,040	$3,512,760	$5,595,827	$8,623,169	
68	*	Nique Clifford	$3,512,520	$3,688,320	$3,864,000	$6,155,352	$9,485,397
77		D'Angelo Russell	$5,104,000				
							
							
		Tristen Newton	$2,191,897	$2,296,271			
	Totals:		$209,280,254	$221,346,841	$116,870,866	$156,656,604	$9,485,397
	Salary Cap:		-$54,633,254				
	Hard Cap:		$7,225,546				
							
							
✉		Boston Celtics					
94	*	Jayson Tatum	$46,394,100	$49,873,658	$53,353,215		
83	*	Derrick White	$46,394,100	$49,873,658	$53,353,215	$56,832,773	$60,312,330
76	*	Goga Bitadze	$5,000,000	$4,500,000	$4,000,000		
76	*	Jordan Poole	$12,000,000	$12,000,000			
76	*	Nickeil A Walker	$15,909,305	$14,636,435	$13,363,565	$12,090,695	
75	*	Anthony Black	$7,970,028	$10,105,996	$14,491,998		
75	*	Kyle Kuzma	$21,477,272	$19,431,819			
75	*	Dayron Sharpe	$13,159,305	$11,886,435	$10,613,565	$9,340,695	
73	*	Julian Champagnie	$3,000,000	$3,000,000			
73	*	Dante Exum	$2,727,130	$2,000,000	$1,272,870		
72	*	Donovan Clingan	$5,742,480	$6,015,600	$7,669,890	$11,213,379	
70	*	Derik Queen	$4,655,040	$4,887,720	$5,120,400	$7,849,573	$11,758,660
66	*	Jordan Walsh	$2,221,677	$2,406,205			
64	*	AJ Green	$2,301,587				
							
		Jeremiah R Earl	$1,157,153				
		Brandon Boston	$1,157,153				
	Totals:		$191,266,330	$190,617,526	$163,238,718	$97,327,115	$72,070,990
	Salary Cap:		-$36,619,330				
	Hard Cap:		$25,239,470				
							
							
✉		Charlotte Hornets					
86	*	LaMelo Ball	$38,070,000	$40,890,000	$43,710,000	$46,860,000	
83	*	Julius Randle	$37,000,000	$34,500,000	$32,000,000	$29,500,000	$27,000,000
80	*	DeMar DeRozan	$24,050,000	$22,100,000			
79	*	Miles Bridges	$27,000,000	$25,000,000	$23,000,000	$21,000,000	
79	*	Brandon Miller	$11,968,400	$15,104,121	$21,221,290		
77	*	Grant Williams	$13,645,500	$14,265,750			
77	*	Mark Williams	$6,276,531	$8,774,591			
77		Chris Paul	$8,000,000				
76	*	James Wiseman	$4,630,813	$5,787,966	$6,945,119		
75	*	Nick Richards	$5,000,000				
74	*	Tre Mann	$10,000,000	$9,500,000	$9,000,000	$8,500,000	$8,000,000
71	*	Jeremiah Fears	$5,715,120	$6,001,080	$6,286,920	$8,342,743	$12,255,489
73	*	Tristan Da Silva	$3,809,520	$3,991,200	$6,138,466	$9,324,330	
68	*	Pelle Larsson	$2,191,897	$2,296,271	$2,486,995		
66	*	Nick Smith Jr	$2,710,303	$4,889,387	$7,739,899		
		Keon Johnson	$1,600,000	$2,000,000			
	Totals:		$201,668,084	$195,100,366	$158,528,689	$123,527,073	$47,255,489
	Salary Cap:		-$47,021,084				
	Hard Cap:		$14,837,716				
							
							
✉		Chicago Bulls					
78	*	Walker Kessler	$4,878,938	$7,064,703			
75	*	Kevin Huerter	$17,991,071				
75	*	Patrick Williams	$15,000,000	$15,000,000	$15,000,000	$15,000,000	
75	*	Kel'el Ware	$4,923,720	$5,158,080	$7,370,897	$10,931,040	
75	*	Jaime Jaquez Jr	$3,861,594	$5,939,132	$9,021,541		
74	*	Max Christie	$8,464,000	$7,786,880	$7,163,930		
70	*	Jaylon Tyson	$3,638,160	$3,811,800	$5,870,172	$8,957,882	
70	*	Kasparas Jakucionis	$7,520,040	$7,896,240	$8,271,960	$10,505,389	$15,138,266
69	*	Jalen H Schifino	$4,064,584	$6,243,200	$9,439,718		
67	*	Reed Sheppard	$13,197,720	$13,826,040	$17,434,637	$24,408,492	
67	*	Sidy Cissoko	$2,221,677				
67	*	Luka Garza	$1,500,000	$1,500,000	$1,500,000		
64	*	Tyler Smith	$3,218,760	$3,372,120	$5,547,138	$8,586,970	
62	*	Tyler Kolek	$1,955,377	$2,296,271			
60	*	Nikola Djurisic	$2,191,897	$2,296,271	$2,486,995		
		Terry Rozier	$1,272,870				
		Trentyn Flowers	$1,955,377				
		Anton Watson	$1,955,377				
		Maxi Kleber	$11,000,000				
		Aleksej Pokusevski	$5,000,000				
		Landry Shamet	$11,750,000				
		Colby Jones	$2,221,677				
		Vasilije Micic	$8,109,150				
		Cody Martin	$8,680,000				
		Jevon Carter	$6,809,524				
	Totals:		$153,381,513	$82,190,737	$89,106,988	$78,389,773	$15,138,266
	Salary Cap:		$1,265,487				
	Hard Cap:		$63,124,287				
							
							
✉		Cleveland Cavaliers					
90	*	Donovan Mitchell	$46,394,100	$49,873,658	$53,353,215		
88	*	Evan Mobley	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
81	*	Mikal Bridges	$24,900,000				
79	*	Alex Caruso	$30,000,000	$31,000,000	$32,000,000	$33,000,000	$34,000,000
78	*	Malik Beasley	$5,000,000	$5,000,000	$5,000,000	$5,000,000	
77	*	Caris Levert	$9,104,000	$10,376,870	$11,649,740	$12,922,610	
76	*	Mitchell Robinson	$12,954,546				
76	*	Ayo Dosunmu	$7,518,518				
74	*	Isaac Okoro	$13,500,000	$14,500,000	$15,500,000	$16,500,000	
73	*	Jake LaRavia	$5,163,127	$7,362,619			
73	*	Georges Niang	$8,200,000				
72	*	Dean Wade	$6,623,456				
71	**	Craig Porter	$2,000,000	$2,100,000	$3,000,000		
60		Nae'Qwan Tomlin	$1,272,870	$1,272,870			
							
		Jaxson Hayes	$1,272,870				
	Totals:		$212,565,237	$163,047,398	$164,963,968	$114,783,254	$84,260,275
	Salary Cap:		-$57,918,237				
	Hard Cap:		$3,940,563				
							
							
✉		Dallas Mavericks					
96	*	Luka Doncic	$45,999,660	$48,967,380			
82	*	Trey Murphy III	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
80	*	Lauri Markkanen	$41,500,000	$44,612,500	$47,958,438	$51,555,320	$55,421,969
77	*	Tyus Jones	$11,500,000	$12,000,000	$12,500,000	$13,000,000	
77	*	Saddiq Bey	$6,425,000	$6,425,000	$7,425,000		
77	*	Daniel Gafford	$14,386,320				
77	*	Onyeka Okongwu	$15,000,000	$16,120,000	$16,880,000		
75	*	Keon Ellis	$18,100,000	$19,450,000	$20,800,000	$22,150,000	
70	*	Dalton Knecht	$4,010,160	$4,201,080	$6,452,860	$9,756,724	
70	*	Isaiah Collier	$3,492,480	$3,658,560	$5,641,500	$8,648,420	
66	*	Dwight Powell	$4,000,000				
62	**	Cam Spencer	$1,600,000	$2,000,000			
							
							
							
	Totals:		$204,675,370	$198,995,901	$162,118,811	$152,471,108	$105,682,244
	Salary Cap:		-$50,028,370				
	Hard Cap:		$11,830,430				
							
							
✉		Denver Nuggets					
99	*	Nikola Jokic	$55,224,526	$59,033,114	$62,841,702		
87	*	Pascal Siakam	$45,339,630	$48,502,860	$51,666,090	$49,986,942	
83	*	Jamal Murray	$46,394,100	$49,873,658	$53,353,215	$56,832,773	$60,312,330
82	*	Norman Powell	$20,482,758				
81	*	CJ McCollum	$30,666,666				
76		Kevin Love	$2,500,000				
74		Ben Simmons	$2,000,000				
64		Pat Connaughton	$1,272,870				
72		Kyle Lowry	$1,272,870				
65	*	Jalen Pickett	$2,221,677	$2,406,205			
65	*	Hunter Tyson	$2,221,677	$2,406,205			
66	*	Noah Penda	$2,783,880	$2,923,560	$3,062,640	$5,528,065	$8,789,623
							
							
							
	Totals:		$212,380,654	$165,145,602	$170,923,647	$112,347,780	$69,101,953
	Salary Cap:		-$57,733,654				
	Hard Cap:		$4,125,146				
							
							
✉		Detroit Pistons					
97	*	Giannis Antetokounmpo	$57,604,894	$62,213,285	$66,821,676		
90	*	Kevin Durant	$54,708,608				
89	*	James Harden	$39,006,071	$41,727,424			
82	*	Jarrett Allen	$20,000,000				
78		Al Horford	$3,000,000	$3,250,000			
77	*	DeAnthony Melton	$13,000,000	$13,000,000	$13,000,000		
75	*	Duncan Robinson	$2,800,000	$4,000,000	$5,200,000		
75	*	Marvin Bagley	$1,600,000	$2,000,000			
74	*	Corey Kispert	$2,700,000	$3,900,000	$5,100,000	$6,300,000	
74	*	Steven Adams	$1,731,000	$2,150,130	$3,423,000	$4,695,870	
74	*	Jose Alvarado	$5,000,000	$5,000,000	$5,000,000		
73		Josh Okogie	$1,272,870	$2,545,740			
70	*	Ousmane Dieng	$1,273,000	$2,545,870	$3,818,740	$5,091,640	
70		Jay Huff	$1,272,870	$2,545,870			
66		Javonte Green	$1,272,870				
		Karlo Matkovic	$1,272,870	$1,272,870			
		Daniel Theis	$2,250,000				
		Amir Coffey	$1,300,000	$1,300,000	$2,200,000	$3,200,000	
		Kobe Brown	$2,654,692				
		Spencer Dinwiddie	$1,300,000	$1,300,000	$2,400,000		
	Totals:		$215,019,745	$148,751,189	$106,963,416	$19,287,510	$0
	Salary Cap:		-$60,372,745				
	Hard Cap:		$1,486,055				
							
							
✉		Golden State Warriors					
92	*	Joel Embiid	$55,224,526	$59,033,114			
86	*	Ja Morant	$39,446,090	$42,166,510	$44,886,930		
82	*	Brandon Ingram	$46,394,100	$49,873,658	$53,353,215	$56,832,773	
80	*	Draymond Green	$25,892,857	$27,678,571			
76	*	Klay Thompson	$19,000,000	$20,000,000			
75	*	Robert Williams	$13,285,713				
73		Oshae Brissett	$1,272,870				
71	*	Collin Murray Boyles	$5,157,960	$5,416,080	$5,673,840	$8,107,918	$12,024,042
70	*	Gui Santos	$2,221,677				
69		Mason Plumlee	$1,272,870				
69	*	Yang Hansen	$3,991,320	$4,190,520	$4,390,320	$6,752,312	$10,256,762
60	*	Alijah Martin	$2,296,274	$2,411,090	$2,525,901	$2,735,698	
							
							
							
	Totals:		$215,456,257	$210,769,543	$110,830,206	$74,428,701	$22,280,804
	Salary Cap:		-$60,809,257				
	Hard Cap:		$1,049,543				
							
							
✉		Houston Rockets					
85	*	Tyler Herro	$31,000,000	$33,000,000			
84	*	Alperen Sengun	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
83	*	Amen Thompson	$9,690,212	$12,258,119	$17,394,270		
76	*	Derrick Jones Jr	$6,450,000	$6,933,750			
76	*	Mike Conley	$10,243,902				
75	*	Kentavious C Pope	$19,000,000	$19,000,000			
75	*	Precious Achiuwa	$6,500,000				
74	*	Peyton Watson	$4,356,476	$6,534,714			
72	*	Jonathan Mogbo	$2,191,897	$2,296,271	$2,486,995		
71	*	Ryan Rollins	$1,600,000	$2,000,000			
66	*	Adou Thiero	$2,983,320	$3,132,360	$3,282,000	$5,910,882	$9,274,174
60	*	Cam Christie	$2,250,000	$2,250,000	$2,500,000	$3,000,000	
60	*	Tyrese Proctor	$2,296,274	$2,411,090	$2,525,901	$2,735,698	
							
							
		Bradley Beal	$53,666,270	$57,128,610			
		Caleb Martin	$4,500,000	$4,000,000	$4,000,000		
	Totals:		$185,146,199	$192,506,295	$76,650,179	$59,007,224	$59,534,449
	Salary Cap:		-$30,499,199				
	Hard Cap:		$31,359,601				
							
							
✉		Indiana Pacers					
90	*	Tyrese Haliburton	$38,070,000	$40,890,000	$43,710,000	$46,860,000	
86	*	DeAaron Fox	$37,096,620				
85	*	Jimmy Butler	$54,036,759	$58,089,516	$61,569,073	$65,048,631	
79	*	Tari Eason	$5,675,766	$8,014,181			
77	*	Santi Aldama	$5,940,797				
75	*	Brandon Clarke	$6,500,000				
74		Royce O'Neale	$1,272,870				
72	*	Terance Mann	$1,272,870	$2,545,740			
69	*	Ben Sheppard	$2,790,889	$5,031,973	$7,930,389		
69	*	Walter Clayton	$3,811,560	$4,002,000	$4,193,040	$6,457,282	$9,853,812
66		Pat Spencer	$1,272,870				
62		Daniss Jenkins	$1,272,870				
61		Dylan Cardwell	$1,272,870	$1,272,870			
							
							
		Alec Burks	$1,272,870				
		Drew Eubanks	$1,272,870				
		Jared Butler	$1,272,870				
		Dario Saric	$1,272,870				
	Totals:		$165,378,221	$119,846,280	$117,402,502	$118,365,913	$9,853,812
	Salary Cap:		-$10,731,221				
	Hard Cap:		$51,127,579				
							
							
✉		Los Angeles Clippers					
87	*	Damian Lillard	$58,545,211	$63,228,828			
78	*	Wendell Carter Jr	$10,850,000				
75	*	Stephon Castle	$9,560,520	$10,015,920	$12,670,139	$17,978,927	
75	*	Jaylen Wells	$2,191,897	$2,296,271	$2,486,995		
74	*	Alex Sarr	$10,603,560	$11,108,880	$14,041,625	$19,826,775	
73	*	Matisse Thybulle	$11,550,000				
72	*	Adem Bona	$2,191,897	$2,296,271	$2,486,995		
72	**	Aaron Holiday	$5,000,000	$6,000,000	$7,000,000		
71	*	Kobe Bufkin	$4,503,668	$6,904,124	$10,342,377		
71	*	Ziaire Williams	$5,000,000	$5,000,000	$5,000,000	$4,900,000	
70	*	Dom Barlow	$4,000,000	$4,000,000			
69		Seth Curry	$1,272,870				
68	*	Nolan Traore	$3,108,120	$3,263,400	$3,418,800	$5,979,481	$9,339,949
65	*	Chris Livingston	$2,221,677	$2,406,205			
							
		Lonnie Walker	$1,600,000	$2,000,000			
		Gary Trent Jr	$2,500,000	$3,200,000			
		Maxwell Lewis	$2,221,677	$2,406,205			
		Josh Christopher	$1,620,000	$1,740,000			
		Davis Bertans	$2,000,000				
		Josh Green	$13,666,667	$14,679,012			
	Totals:		$154,207,764	$140,545,116	$57,446,931	$48,685,183	$9,339,949
	Salary Cap:		$439,236				
	Hard Cap:		$62,298,036				
							
							
✉		Los Angeles Lakers					
92	*	Anthony Davis	$57,604,894	$62,213,285	$66,821,676		
79	*	PJ Washington	$14,152,174				
77	*	Obi Toppin	$5,500,000	$5,500,000	$5,500,000		
76	*	Rui Hachimura	$18,259,259				
76	*	Quentin Grimes	$28,872,595	$31,038,040	$33,203,484	$35,368,929	$37,534,373
76		Jonas Valanciunas	$1,272,870	$1,272,870			
76	*	Aaron Wiggins	$14,104,000	$15,161,800	$16,219,600	$17,277,400	
75	*	Lonzo Ball	$10,000,000	$10,750,000	$11,500,000	$12,250,000	
74	*	Jarace Walker	$6,665,406	$8,478,396	$12,276,717		
72	*	Jarred Vanderbilt	$11,571,429	$12,428,571	$13,285,714		
72	*	Rob Dillingham	$7,863,240	$8,237,880	$10,445,633	$14,979,038	
72	*	Yves Missi	$2,638,200	$2,763,960	$4,988,948	$7,982,317	
71		Taurean Prince	$4,104,000	4,411, 800			
71	*	Khaman Maluach	$6,016,080	$6,316,680	$6,617,160	$8,436,880	$12,334,719
70	*	Terrence Shannon	$2,657,760	$2,784,240	$5,025,553	$7,990,629	
		Delon Wright	$3,000,000				
		Melvin Ajinca	$2,191,897	$2,296,271			
		Blake Wesley	$4,726,328				
		Jaxson Hayes	$1,157,153				
		Gabe Vincent	$11,500,000				
	Totals:		$213,857,285	$169,241,993	$185,884,485	$104,285,193	$49,869,092
	Salary Cap:		-$59,210,285				
	Hard Cap:		$2,648,515				
							
							
✉		Memphis Grizzlies					
87	*	Jaren Jackson Jr	$23,413,395				
87	*	Trae Young	$45,999,660	$48,967,380			
86	*	Kyrie Irving	$42,962,963				
83	*	Ivica Zubac	$46,394,100	$49,873,657	$53,353,214	$56,832,771	$60,312,328
80	*	Herbert Jones	$13,937,574	$14,898,786			
75	*	Bogdan Bogdanovic	$16,020,000	$16,020,000			
73		Justin Champagnie	$1,157,153				
72	**	Bruce Brown	$6,450,000	$6,933,750			
65	*	Andre Jackson Jr	$2,221,677	$2,406,205			
62	*	Baylor Scheierman	$2,191,897	$2,296,271	$2,486,995		
71	*	Egor Demin	$4,201,080	$4,411,200	$4,621,200	$7,098,163	$10,732,422
68	*	Will Riley	$2,763,960	$2,902,080	$3,040,320	$5,487,778	$8,780,445
							
							
							
		Nassir Little	$7,250,000	$7,750,000			
	Totals:		$214,963,459	$156,459,329	$63,501,729	$69,418,712	$79,825,195
	Salary Cap:		-$60,316,459				
	Hard Cap:		$1,542,341				
							
							
✉		Miami Heat					
86	*	Tyrese Maxey	$37,783,025	$40,419,050	$43,055,075	$45,691,100	
80	*	John Collins	$33,802,817	$31,267,606	$28,732,394	$26,197,183	
79	*	Khris Middleton	$34,012,345				
76	*	Jonathan Kuminga	$38,661,750	$41,561,381	$44,461,013		
76	*	Cole Anthony	$13,100,000	$13,100,000			
74	*	Jordan Clarkson	$14,285,714				
70		Reggie Jackson	$2,112,481				
70	*	Nikola Jovic	$4,445,417	$6,592,553			
69	*	Landry Shamet	$1,157,153	$1,157,153			
68	*	Jabari Walker	$1,274,000	$2,500,000	$2,750,000	$4,024,000	
67	*	Ajay Mitchell	$12,830,000	$12,666,667	$12,503,333		
71	*	Carter Bryant	$6,889,200	$7,233,720	$7,578,240	$9,639,522	$13,958,028
							
							
							
	Totals:		$200,353,902	$156,498,130	$139,080,055	$85,551,805	$13,958,028
	Salary Cap:		-$45,706,902				
	Hard Cap:		$16,151,898				
							
							
✉		Milwaukee Bucks					
89	*	Devin Booker	$53,298,000	$57,246,000	$61,194,000		
89	*	Karl Anthony Towns	$53,298,000	$57,246,000	$61,194,000		
86	*	Zion Williamson	$39,446,090	$42,166,510	$44,886,930		
79	*	Josh Giddey	$38,661,750	$41,561,381	$44,461,013	$47,360,644	
75		Guerschon Yabusele	$1,272,870	$1,272,870			
74		Gary Trent Jr	$1,272,870	$1,272,870			
73	*	Bub Carrington	$8,657,280	$9,069,600	$11,491,183	$16,386,427	
73	*	VJ Edgecombe	$11,108,880	$11,663,880	$12,219,840	$15,445,878	$21,809,580
73	*	Paul Reed	$1,600,000	$2,000,000			
72		NahShon Hyland	$1,272,870	$1,272,870			
71		Jaxson Hayes	$1,272,870	$1,272,870			
69		Jaden Hardy	$1,272,870	$1,368,335			
							
							
							
		Julian Phillips	$2,221,677				
		Mark Sears	$1,272,870				
	Totals:		$215,928,897	$227,413,186	$235,446,966	$79,192,949	$21,809,580
	Salary Cap:		-$61,281,897				
	Hard Cap:		$576,903				
							
							
✉		Minnesota Timberwolves					
91	*	Anthony Edwards	$38,070,000	$40,890,000	$43,710,000	$46,860,000	
90	*	Stephen Curry	$59,606,817				
85	*	Kristaps Porzingis	$30,731,707				
84	*	Jalen Johnson	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
79	*	Jaden McDaniels	$24,393,104	$26,200,001	$28,006,898	$29,813,790	
75		Andre Drummond	$4,000,000	$4,300,000			
75	**	Luke Kennard	$7,000,000	$6,000,000	$5,000,000		
75		Cody Martin	$1,272,870	$2,545,740			
74		Gary Payton II	$2,100,000	$3,372,870			
73		Kyle Anderson	$1,272,870				
70	*	Josh Minott	$2,187,699				
69		Patrick Mills	$1,272,870				
67	*	Bruno Fernando	$2,853,260				
							
							
	Totals:		$213,422,947	$124,869,992	$121,177,911	$124,034,434	$50,260,275
	Salary Cap:		-$58,775,947				
	Hard Cap:		$3,082,853				
							
							
✉		Montreal Mastodons					
77	*	Collin Gillespie	$13,659,305	$12,386,435	$11,113,565	$9,840,695	
78	*	Zach Edey	$6,576,120	$6,889,320	$8,763,216	$12,689,137	
75	*	Davion Mitchell	$13,500,000	$12,500,000	$11,500,000	$10,500,000	
74	*	Keldon Johnson	$17,500,000	$17,500,000			
73	*	Ronald Holland II	$6,045,000	$6,332,760	$8,067,937	$11,738,848	
72	*	Vince Williams Jr	$2,301,587	$2,489,752			
72	*	Mouhamed Gueye	$1,300,000	$1,300,000			
72	*	Kon Knueppel	$9,069,840	$9,523,080	$9,976,560	$12,640,302	$18,025,071
71	*	Noa Essengue	$5,429,520	$5,701,200	$5,972,760	$8,230,464	$12,148,165
71	*	Moses Moody	$8,000,000	$8,000,000	$8,000,000	$8,000,000	$8,000,000
71	*	Devin Carter	$2,000,000	$2,000,000	$2,000,000	$2,000,000	
70	*	Josh Green	$3,000,000	$3,000,000	$3,000,000		
68	*	Moussa Diabate	$4,000,000	$5,000,000	$6,000,000		
67	*	Noah Clowney	$3,398,406	$5,413,661	$8,342,451		
60	*	Bobi Klintman	$2,191,897	$2,296,271	$2,486,995		
		Guerschon Yabusele	$2,314,306				
		D'Angelo Russell	$22,000,000				
		Richaun Holmes	$1,272,870				
		Max Shulga	$1,400,000	$1,400,000	$1,400,000		
		Jericho Sims	$1,600,000	$2,000,000			
		Johnny Juzang	$2,700,000	$1,800,000			
		Jay Huff	$8,000,000				
		Jalen Wilson	$2,000,000				
		Paul Reed	$8,109,150				
	Totals:		$147,368,001	$105,532,479	$86,623,484	$75,639,446	$38,173,236
	Salary Cap:		$7,278,999				
	Hard Cap:		$69,137,799				
							
							
✉		New Orleans Pelicans					
86	*	Franz Wagner	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
84	*	Darius Garland	$39,446,090	$42,166,510	$44,886,930		
80	*	Fred VanVleet	$34,000,000	$31,500,000			
80	*	Deni Avdija	$14,375,000	$13,125,000	$11,875,000		
80	*	Dyson Daniels	$7,707,709	$10,389,992			
76	*	Ausar Thompson	$8,775,162	$11,118,130	$15,854,453		
75	*	Dereck Lively II	$5,253,191	$7,238,897	$10,684,611		
75	*	Cam Whitmore	$3,539,976	$5,458,643	$8,368,099		
75	*	Brandin Podziemski	$3,687,644	$5,678,972	$8,666,111		
72	*	Sam Hauser	$7,100,000	$6,000,000	$6,000,000	$4,900,000	
71	*	Kyshawn George	$4,221,360	$4,422,600	$6,784,268	$10,210,323	
70	*	JaKobe Walter	$2,191,897	$2,296,271	$2,486,995		
70	*	Leonard Miller	$2,221,677	$2,406,205			
69	*	Luke Kornet	$6,400,000	$5,200,000			
							
	Totals:		$177,581,456	$188,562,601	$160,067,480	$62,470,967	$50,260,275
	Salary Cap:		-$22,934,456				
	Hard Cap:		$38,924,344				
							
							
✉		New York Knicks					
89	*	Jalen Brunson	$46,394,100	$49,873,658	$53,353,215	$56,832,773	$60,312,330
82	*	OG Anunoby	$45,339,630	$48,502,860	$51,666,090	$54,829,320	
81	*	Isaiah Hartenstein	$36,250,000	$37,500,000	$39,000,000	$37,507,150	
79	*	Naz Reid	$28,251,578	$26,632,992	$25,002,401	$23,371,810	$21,741,219
78	*	Donte DiVincenzo	$11,990,000	$12,535,000			
77	*	Bobby Portis	$14,104,000	$15,376,870	$16,649,740	$17,922,610	
75		Larry Nance Jr	$1,157,153				
72		Kenrich Williams	$1,272,870	$2,545,740			
71		Nicolas Batum	$1,272,870	$2,545,740			
64	*	Pacome Dadiet	$2,619,000	$2,744,040	$4,952,993	$7,924,789	
70	*	Johnny Furphy	$2,966,760	$3,108,000	$5,435,892	$8,490,863	
69	*	Sam Merrill	$1,272,880	$2,545,750	$3,818,620	$5,091,490	
69		Jevon Carter	$1,272,870				
65		Xavier Tillman	$1,272,870	$2,545,740			
60	*	Ryan Nembhard	$2,296,274	$2,411,090	$2,525,901	$2,735,698	
		Eric Gordon	$1,272,870				
	Totals:		$199,005,725	$208,867,480	$202,404,852	$214,706,503	$82,053,549
	Salary Cap:		-$44,358,725				
	Hard Cap:		$17,500,075				
							
							
✉		Oklahoma City Thunder					
96	*	Shai G Alexander	$38,333,050	$40,806,150			
86	*	Jalen Williams	$6,580,997	$9,055,452			
83	*	Desmond Bane	$36,725,670	$39,446,090	$42,166,510	$44,886,930	
82	*	Chet Holmgren	$13,731,368	$17,919,435			
81	*	Rudy Gobert	$46,655,173				
77	*	Dorian F Smith	$6,000,000	$6,000,000			
76	*	Kris Dunn	$12,000,000	$11,000,000	$11,500,000	$10,500,000	
74	*	Isaiah Joe	$37,000,000				
73	*	Jaylin Williams	$2,187,699				
72	*	Jordan Hawkins	$4,741,216	$7,021,740	$10,469,414		
72		Chris Boucher	$2,100,000	$2,100,000			
67	*	Ricky Council IV	$2,000,000				
67	*	Jaylen Clark	$1,300,000	$1,300,000			
66	*	Kris Murray	$3,132,254	$5,315,436	$8,265,502		
71		Duop Reath	$1,272,870				
	Totals:		$211,760,297	$139,964,303	$72,401,426	$55,386,930	$0
	Salary Cap:		-$57,113,297				
	Hard Cap:		$4,745,503				
							
							
✉		Orlando Magic					
91	*	Kawhi Leonard	$50,000,000	$50,300,000			
83	*	Paolo Banchero	$15,334,769	$19,935,199			
82	*	Austin Reaves	$13,937,574	$14,898,786			
81	*	Aaron Gordon	$24,719,101	$26,573,034	$28,426,966	$30,280,899	
78	*	Devin Vassell	$27,000,000	$27,000,000	$24,652,174	$27,000,000	
78	*	Luguentz Dort	$17,722,222	$17,722,222			
78	*	Dillon Brooks	$21,124,110	$19,992,727			
77	*	Clint Capela	$5,075,337	$5,329,104	$5,595,559		
75	*	Naji Marshall	$7,000,000	$6,500,000			
75	*	Marcus Smart	$21,336,856				
74	*	Kevon Looney	$1,600,000	$2,000,000			
67	*	Jock Landale	$1,300,000	$2,572,870	$2,627,130		
64	*	Dillon Jones	$2,191,897	$2,296,271	$2,486,995		
60	*	Johni Broome	$2,296,274	$2,411,090	$2,525,901	$2,735,698	
							
		KJ Martin	$1,600,000	$2,000,000			
	Totals:		$212,238,140	$199,531,303	$66,314,725	$60,016,597	$0
	Salary Cap:		-$57,591,140				
	Hard Cap:		$4,267,660				
							
							
✉		Philadelphia 76ers					
92	*	LeBron James	$54,126,450	$58,185,934			
87	*	Jaylen Brown	$53,298,000	$57,246,000	$61,194,000	$65,604,000	
83	*	Josh Hart	$19,472,240	$20,923,760	$22,375,280		
82	*	Nikola Vucevic	$21,481,481				
80	*	Cameron Johnson	$21,570,652	$23,625,000			
80	*	Coby White	$12,888,889				
78	*	Kelly Oubre Jr	$8,500,000	$9,000,000	$9,500,000		
78	**	Brook Lopez	$9,000,000	$9,000,000	$9,000,000		
77	*	Miles McBride	$4,333,333	$3,956,523			
73	*	Quinten Post	$1,955,377	$2,296,271			
68	*	Christian Koloko	$1,500,000	$1,500,000			
68	*	KJ Simpson	$1,955,377	$2,296,271			
62	*	Bronny James	$2,753,280	$2,884,440	$5,200,646	$8,196,218	
							
							
	Totals:		$212,835,079	$190,914,199	$107,269,926	$73,800,218	$0
	Salary Cap:		-$58,188,079				
	Hard Cap:		$3,670,721				
							
							
✉		Phoenix Suns					
83	*	Zach LaVine	$45,999,660	$48,967,380			
81	*	Michael Porter Jr	$38,333,050	$40,806,150			
79	*	Christian Braun	$4,921,797	$7,092,309			
79	*	Jakob Poeltl	$19,500,000	$19,500,000			
77	*	Andrew Nembhard	$2,187,451				
76	*	Jusuf Nurkic	$19,375,000				
76	*	Aaron Nesmith	$11,000,000	$11,000,000			
75	*	Bilal Coulibaly	$7,275,682	$9,240,116	$13,315,007		
75		Kelly Olynyk	$5,000,000				
75	*	Cooper Flagg	$13,825,920	$14,517,480	$15,208,680	$19,178,146	$26,849,404
62	*	Antonio Reeves	$2,191,897	$2,296,271	$2,486,995		
72		Jalen Smith	$5,795,185	$6,275,185	$6,755,185		
72	*	Tre Johnson	$8,237,640	$8,649,600	$9,061,680	$11,490,211	$16,476,963
71	*	Julian Strawther	$2,674,148	$4,826,838	$7,722,940		
64	*	Cody Williams	$5,455,560	$5,715,360	$7,584,283	$11,141,312	
		Josh Richardson	$1,157,153				
		Aleksej Pokusevski	$3,784,076				
		Jevon Carter	$3,784,076				
		Xavier Tillman	$4,000,000	$3,000,000			
	Totals:		$204,498,295	$181,886,689	$62,134,770	$41,809,669	$43,326,367
	Salary Cap:		-$49,851,295				
	Hard Cap:		$12,007,505				
							
							
✉		Portland Trailblazers					
79	*	Deandre Ayton	$35,550,814				
77	*	Jerami Grant	$32,000,001	$34,206,898	$36,413,790		
77	*	Toumani Camara	$2,221,677	$2,406,205			
76	*	Shaedon Sharpe	$8,399,983	$11,264,377			
75	*	Jaden Ivey	$10,107,163	$13,402,098			
74	*	Grayson Allen	$18,543,750	$19,456,250			
73	*	Scoot Henderson	$10,747,994	$13,585,465	$19,182,676		
72	*	Matas Buzelis	$7,178,400	$7,519,920	$9,550,298	$13,761,979	
65	*	Rayan Rupert	$2,221,677				
62	*	Oso Ighodaro	$1,955,377	$2,296,271			
62	*	Ulrich Chomche	$2,191,897	$2,296,271	$2,486,995		
71	*	Cedric Coward	$6,332,520	$6,649,560	$6,966,000	$8,874,684	$12,912,665
68	*	Danny Wolf	$3,658,800	$3,841,680	$4,024,440	$6,205,687	$9,513,318
66	*	Ryan Kalkbrenner	$3,237,480	$3,399,480	$3,560,880	$6,042,814	$9,396,576
60		Kobe Sanders	$1,272,870				
		Duop Reath	$2,221,677				
		Caleb Houstan	$2,187,451				
		Jock Landale	$8,000,000				
	Totals:		$155,807,854	$120,324,475	$82,185,079	$34,885,164	$31,822,559
	Salary Cap:		-$1,160,854				
	Hard Cap:		$60,697,946				
							
							
✉		Sacramento Kings					
87	*	Domantas Sabonis	$44,936,000	$48,072,000	$51,208,000		
80	*	Collin Sexton	$18,975,000				
79	*	Jalen Duren	$6,483,144	$8,966,189			
78	*	Andrew Wiggins	$28,223,215	$30,169,644			
78	*	Malik Monk	$14,000,000	$14,000,000	$14,000,000	$14,000,000	
78	*	Anfernee Simons	$27,678,571				
76	*	Keegan Murray	$11,144,093	$14,699,059			
66	*	Bol Bol	$4,000,000	$4,000,000	$4,000,000		
76	**	TJ McConnell	$8,500,000	$8,000,000	$7,500,000		
76	*	Cameron Payne	$1,604,000	$2,876,870	$4,149,740	$5,422,610	
75	*	Harrison Barnes	$19,000,000				
66	*	John Konchar	$6,165,000	$6,165,000			
69	*	Asa Newell	$4,900,320	$5,145,360	$5,390,640	$7,983,539	$11,903,457
60	*	Brooks Barnhizer	$2,296,274	$2,411,090	$2,525,901	$2,735,698	
							
	Totals:		$197,905,617	$144,505,212	$88,774,281	$30,141,847	$11,903,457
	Salary Cap:		-$43,258,617				
	Hard Cap:		$18,600,183				
							
							
✉		San Diego Caravels					
91	*	Victor Wembanyama	$13,376,695	$16,868,013	$23,615,218		
86	*	Cade Cunningham	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
85	*	Bam Adebayo	$37,096,620				
79	*	Payton Pritchard	$7,232,143	$7,767,857	$8,303,571		
78		Tobias Harris	$18,572,971				
78	**	Dennis Schroder	$13,939,537	$12,666,667	$11,393,797		
77	*	Tre Jones	$22,726,182				
75		Buddy Hield	$1,600,000				
75		Tim Hardaway Jr	$5,886,435	$4,613,565			
74	*	Moritz Wagner	$8,909,305	$7,636,435	$6,363,565	$5,090,695	
74	**	Jonathan Isaac	$13,245,740	$11,972,870	$10,700,000		
71	*	Justin Edwards	$1,955,377	$2,296,271			
70	*	Ryan Dunn	$2,674,080	$2,801,640	$5,054,159	$8,000,734	
67	*	Neemias Queta	$2,000,000				
79		Bradley Beal	$1,272,870	$1,272,870			
	Totals:		$189,149,705	$109,457,569	$109,891,323	$60,452,073	$50,260,275
	Salary Cap:		-$34,502,705				
	Hard Cap:		$27,356,095				
							
							
✉		Toronto Raptors					
84	*	Scottie Barnes	$38,661,750	$41,561,381	$44,461,013	$47,360,644	$50,260,275
82	*	RJ Barrett	$27,705,357	$29,616,071			
81	*	Myles Turner	$45,000,000	$48,375,000	$51,750,000	$55,125,000	
79	*	Immanuel Quickley	$36,500,000	$38,000,000	$39,500,000	$41,000,000	
75	*	Cason Wallace	$5,820,487	$7,421,121	$10,849,678		
75	*	Gradey Dick	$4,990,379	$7,131,251	$10,575,645		
73	*	Ochai Agbaji	$6,383,525	$8,879,483			
64	*	Tony Bradley	$1,700,000	$1,800,000	$1,900,000	$2,000,000	
70	*	DaRon Holmes	$2,847,600	$2,983,680	$5,373,608	$8,431,191	
70	*	Jaden Springer	$2,000,000	$2,000,000	$2,000,000		
69	*	Dariq Whitehead	$1,722,632	$2,995,502	$4,268,372	$5,541,242	
68	*	Jamal Shead	$2,191,897	$2,296,271	$2,486,995		
70	*	Thomas Sorber	$4,422,360	$4,643,520	$4,864,920	$7,462,788	$11,231,496
							
							
	Totals:		$179,945,987	$197,703,280	$178,030,231	$166,920,865	$61,491,771
	Salary Cap:		-$25,298,987				
	Hard Cap:		$36,559,813				
							
							
✉		Utah Jazz					
80	*	Jrue Holiday	$33,600,000	$33,600,000	$32,200,000		
77	*	Ty Jerome	$13,842,847	$12,685,694			
75	*	Max Strus	$15,936,452	$16,660,836			
75	*	Zach Collins	$18,080,496				
75	*	Zaccharie Risacher	$11,808,240	$12,370,680	$15,611,798	$21,934,576	
75	*	Keyonte George	$4,278,754	$6,563,608	$9,878,230		
74	*	Taylor Hendricks	$6,126,859	$7,805,619	$11,357,175		
74	*	Dylan Harper	$12,370,320	$12,989,040	$13,607,760	$17,172,994	$24,128,057
73	*	Jeremy Sochan	$7,096,231	$9,615,393			
71	*	Jared McCain	$3,090,480	$3,237,120	$5,493,394	$8,542,228	
69	*	Zeke Nnaji	$8,177,778	$7,466,667	$7,466,667		
69	*	AJ Johnson	$1,955,377	$2,296,271			
68	*	Brice Sensabaugh	$2,693,460	$4,861,695	$7,730,095		
67	*	Liam McNeeley	$2,884,560	$3,028,560	$3,172,920	$5,720,776	$9,015,943
66	*	Tristan Vukcevic	$9,200,000	$9,700,000	$10,400,000		
		Devin Carter	$4,443,360				
		Craig Porter	$2,221,677				
		Enrique Freeman	$1,955,377				
	Totals:		$159,762,268	$142,881,183	$116,918,039	$53,370,574	$33,144,000
	Salary Cap:		-$5,115,268				
	Hard Cap:		$56,743,532				
							
							
✉		Washington Wizards					
82	*	Cam Thomas	$38,661,750	$41,561,381	$44,461,013	$47,360,644	
81	*	Dejounte Murray	$27,539,568	$29,523,536	$31,507,504		
81	*	Paul George	$52,896,235	$56,586,670	$60,277,105		
76	*	Isaiah Stewart	$15,000,000	$15,000,000	$15,000,000		
75	*	Scottie Pippen Jr	$9,000,000	$10,000,000	$11,000,000		
72	*	Tidjane Salaun	$5,182,920	$5,429,760	$7,482,210		
72	*	GG Jackson	$2,221,677	$2,406,205			
72	*	Trayce J Davis	$2,221,677	$2,406,205			
72	*	Ace Bailey	$10,015,680	$10,516,560	$11,017,560	$13,937,214	$19,776,907
71	*	Nikola Topic	$4,677,600	$4,900,560	$7,257,730	$10,821,275	
71	*	Jase Richardson	$3,372,240	$3,540,600	$3,709,320	$6,101,832	$9,445,636
68	*	Joan Beringer	$2,801,280	$2,941,440	$3,081,840	$5,559,640	$8,800,910
66	*	Sandro Mamu	$1,350,000	$1,350,000	$1,350,000	$1,350,000	
65		EJ Liddell	$1,272,870	$1,272,870			
							
		Jonas Valanciunas	$14,000,000	$14,000,000	$14,000,000		"""

PLAYER_REGEX = re.compile(
    r'^\s*'
    r'(?:(?P<rating>\d{2,3})\s*)?'      # Rating
    r'(?P<birds>\*{0,2})\s*'            # Birds
    r'(?P<name>[A-Z][A-Za-z\s\.\']+?)'  # Nome
    r'\s+(?P<contracts>(?:\$[0-9,]+\s*)+)$',
    re.MULTILINE
)

def parse_and_upload():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    blocks = RAW_DATA.split('✉')

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        current_team = next((t for t in TEAMS if t in block), None)
        if not current_team:
            continue

        for match in PLAYER_REGEX.finditer(block):
            raw_name = match.group('name').strip()

            name = PLAYER_NAME_MAP.get(raw_name, raw_name)

            if any(k in name.upper() for k in IGNORE_KEYWORDS):
                continue

            rating = int(match.group('rating')) if match.group('rating') else None
            birds = len(match.group('birds') or "")

            raw_contracts = re.findall(r'\$[0-9,]+', match.group('contracts'))
            cts = [None] * 5

            for i, val in enumerate(raw_contracts[:5]):
                cts[i] = int(val.replace('$', '').replace(',', ''))

            cursor.execute("""
                INSERT INTO players (name, team, rating, birds, ct1, ct2, ct3, ct4, ct5)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    team=excluded.team,
                    rating=excluded.rating,
                    birds=excluded.birds,
                    ct1=excluded.ct1,
                    ct2=excluded.ct2,
                    ct3=excluded.ct3,
                    ct4=excluded.ct4,
                    ct5=excluded.ct5
            """, (
                name, current_team, rating, birds,
                cts[0], cts[1], cts[2], cts[3], cts[4]
            ))

    conn.commit()
    conn.close()
    print("Upload complete. Mapped names used.")

if __name__ == "__main__":
    parse_and_upload()