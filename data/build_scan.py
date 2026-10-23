#!/usr/bin/env python3
"""
Rebuild the North Florida / SE-coast service-supply scan captured 22-23 Oct 2026.

Source: Google Maps local list view (free, no paid API). Rows are transcribed from the
browser extraction performed during the session; format per row is

    Name|phone|rating|w   (w = has website per Maps "Visit ... website" link, - = none)

Fields Google Maps list view does not expose in this layout: review counts. So supply
strength is expressed as operator count, median rating and website presence. Any artifact
built from this file must repeat that limitation.

Run:  python3 build_scan.py
Emit: nefl-supply-scan.csv        (one row per operator listing)
      nefl-supply-scan.json       (market-level aggregates + full rows + assessment)
"""
import csv, json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))

# region: core = Evan's backyard (Duval + Jacksonville Beach + St Johns + Clay + Nassau)
#         fringe = NE Florida outer ring, still drivable
#         out = out-of-area comparison metros (SE coast, GA/NC/SC) - not prospects
DATA = {
"septic tank pumping": {
 "Jacksonville FL": ("core", """
Duck Duck Rooter|(904) 209-9050|4.8|w
Flamingo Septic|(904) 222-7465|4.5|w
Metro Rooter (Wind River)|(904) 567-3775|4.8|w
Dr. Poo Sanitation Solutions|(904) 727-0000|4.9|w
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Bullfrog Septic|(904) 680-5044|5.0|w
Presto Plumbing & Septic|(904) 944-4644|4.8|w
O'Connor's Plumbing & Septic|(904) 767-4059|4.5|w
Septic Specialists LLC|(904) 895-5785|4.5|w
Jax Plumbing & Septic Tank|(904) 786-1380|4.3|w
"""),
 "Jacksonville Beach FL": ("core", """
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Flamingo Septic|(904) 222-7465|4.5|w
Bullfrog Septic|(904) 680-5044|5.0|w
Duck Duck Rooter|(904) 209-9050|4.8|w
Metro Rooter|(904) 567-3775|4.8|w
Dr. Poo Sanitation Solutions|(904) 727-0000|4.9|w
Septic Specialists LLC|(904) 895-5785|4.5|w
"""),
 "Orange Park FL": ("core", """
Florida Pump Service|(904) 269-0202|4.6|w
Duck Duck Rooter|(904) 209-9050|4.8|w
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Flamingo Septic|(904) 222-7465|4.5|w
Grant's Plumbing|(904) 600-0707|4.9|w
Jax Plumbing & Septic Tank|(904) 786-1380|4.3|w
Presto Plumbing & Septic|(904) 944-4644|4.8|w
"""),
 "Fleming Island FL": ("core", """
Flamingo Septic|(904) 222-7465|4.5|w
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Jax Plumbing & Septic Tank|(904) 786-1380|4.3|w
Florida Pump Service|(904) 269-0202|4.6|w
Duck Duck Rooter|(904) 209-9050|4.8|w
Grant's Plumbing|(904) 600-0707|4.9|w
JL Smith Septic Tank|(904) 378-1411|4.5|w
"""),
 "Saint Augustine FL": ("core", """
Moore's Sand and Septic|(904) 824-8939|4.9|w
Burney's Septic Tank Service|(904) 829-2953|4.5|w
East Coast Septic Services|(904) 545-6241|3.3|w
McDaniel's Sand & Septic Tank|(904) 824-1033|4.0|w
Mr. Rooter Plumbing of St. Augustine|(386) 338-0107|4.8|w
Outhouse Septic|(904) 829-1184|5.0|w
"""),
 "Saint Johns FL": ("core", """
Moore's Sand and Septic|(904) 824-8939|4.9|w
Burney's Septic Tank Service|(904) 829-2953|4.5|w
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Duck Duck Rooter|(904) 209-9050|4.8|w
Presto Plumbing & Septic|(904) 944-4644|4.8|w
East Coast Septic Services|(904) 545-6241|3.6|w
A1 Septic Service|-|2.8|w
"""),
 "Nocatee FL": ("core", """
Jacksonville Septic Tank Pumping|(904) 747-8871|4.3|w
Moore's Sand and Septic|(904) 824-8939|4.9|w
Burney's Septic Tank Service|(904) 829-2953|4.5|w
Bullfrog Septic|(904) 680-5044|5.0|w
Flamingo Septic|(904) 222-7465|4.5|w
East Coast Septic Services|(904) 545-6241|3.6|w
Consolidated Utilities|(904) 249-8080|4.0|w
"""),
 "Green Cove Springs FL": ("core", """
J&J Septic|(904) 579-7103|5.0|w
Grant's Plumbing|(904) 600-0707|4.9|w
Metro Rooter|(904) 567-3775|4.8|w
O'Connor's Plumbing & Septic|(904) 767-4059|4.5|w
Presto Plumbing & Septic|(904) 944-4644|4.8|w
A1 Septic Service|-|2.8|w
Tom Hunter Septic|(904) 757-7319|5.0|w
"""),
 "Fernandina Beach FL": ("core", """
Murray Septic Tank|(904) 261-5726|4.8|-
Blockers Septic Service|(904) 225-5265|4.0|w
CJ Bass Plumbing|(904) 838-9935|4.9|w
Flamingo Septic|(904) 222-7465|4.5|w
Ground Control Septic|(912) 390-5555|5.0|w
Dr. Poo Sanitation Solutions|(904) 727-0000|4.9|w
Tom Hunter Septic|(904) 757-7319|5.0|w
"""),
 "Callahan FL": ("fringe", """
K.A. Farmer's Septic Tank|(904) 879-4701|4.8|w
Ron's Septic Tank Services|(904) 445-8102|4.3|-
Hendricks Septic Systems|(904) 879-3823|3.9|-
Flamingo Septic|(904) 222-7465|4.5|w
Florida Pumping|(904) 909-9969|4.4|w
A & H Septic & Site Prep|(904) 718-8459||-
"""),
 "Macclenny FL": ("fringe", """
Terry Crews Septic Tank|(904) 259-7818|4.8|-
Darrell Crews Septic Tank|(904) 923-1241|4.7|w
Superior Septic Services|(904) 838-6500|5.0|w
"""),
 "Lake City FL": ("fringe", """
North Florida Septic|(386) 755-6372|4.6|w
Ford's Septic Tank Service|(386) 755-6288|3.6|-
Gross Septic|(386) 984-0173|4.8|w
Hall's Pump & Well Services|(386) 752-1854|4.5|w
"""),
 "Gainesville FL": ("out", """
Wind River Environmental|(978) 574-7666|4.8|w
Dampier Septic Tank|(352) 378-2659|4.5|w
Newsome Well & Septic|(386) 588-8378|4.6|w
Florida Septic Services|(904) 966-1015|5.0|w
BJ's Septic & Site Work|(352) 234-0805|4.6|w
Branson & Son's Septic|(352) 895-0806|5.0|w
Stephenson Septic Tank Service|(352) 542-8659|4.4|w
"""),
 "Ocala FL": ("out", """
A-1 Payless Septic Service|(352) 732-6800|4.2|w
Hills Septic Service|(352) 648-2654|4.8|w
Moring Septic Tank Services|(352) 629-7286|4.7|-
Ocala Well and Septic|(352) 425-7161|4.9|-
Nu Septic|(352) 679-5382|4.7|w
ABC Septic Pumping of Ocala|(352) 282-5353|4.5|-
Ocala Septic Tank Pumping|(352) 414-4761|2.7|-
"""),
 "Starke FL": ("out", """
Phillip McDonald Plumbing & Septic|(904) 964-3737|4.9|w
Triple S Plumbing|(352) 473-0083|4.5|-
Durrance Pump & Supply|(904) 964-7061|4.3|-
Florida Septic Services|(904) 966-1015|5.0|w
BJ's Septic & Site Work|(352) 234-0805|4.6|w
Terry Crews Septic Tank|(904) 259-7818|4.8|-
East Star Industries|(904) 964-9649||-
"""),
 "Tallahassee FL": ("out", """
Brian's Septic Service|(850) 309-0000|4.6|w
Capital City Septic Services|(850) 536-6919|4.6|w
Apalachee Backhoe & Septic Tank|(850) 877-2824|4.4|w
All Septic Solutions|(850) 491-1924|5.0|w
Southern Septic Solutions|(850) 841-9066|5.0|w
Big Bend Septic Tank Company|(850) 629-0261|4.4|-
Terry West Plumbing|(850) 756-9407|4.8|w
"""),
 "Brunswick GA": ("out", """
Hutcheson Septic|(912) 617-2430|4.8|w
AAA Septic Tank Service of Glynn|(912) 461-6120|4.9|w
Coastal Georgia Septic|(912) 476-0063|5.0|w
Wiggins Septic Service|(912) 223-0700|4.9|-
TideCo Septic & Services|(912) 230-8097|5.0|w
A1 of Glynn Septic Solutions|(912) 399-7143|5.0|w
AAA Septic Tank Service of Glynn|(912) 262-0055|5.0|-
"""),
 "Saint Marys GA": ("out", """
Ground Control Septic|(912) 390-5555|5.0|w
Superior Septic Tank Service|(912) 674-2966|4.9|w
Cox-Shytle Septic Services|(912) 324-1507|4.9|w
AAA Septic Tank Service of Glynn|(912) 461-6120|4.9|w
Blockers Septic Service|(904) 225-5265|4.0|w
Coastal Georgia Septic|(912) 476-0063|5.0|w
Murray Septic Tank|(904) 261-5726|4.8|-
"""),
 "Waycross GA": ("out", """
Satilla Septic|(912) 286-4231|4.9|w
Sammy's Septic Service|(912) 288-3631|4.2|w
Jake's Septic Solutions|(912) 286-8280|5.0|w
Peacock Septic Tank Service|(912) 221-2229|5.0|w
Bob's Septic Tank Co|(912) 283-6727|4.8|-
Cox-Shytle Septic Services|(912) 324-1507|4.9|w
Outdoor Septic & Services|(912) 816-5546|5.0|-
"""),
 "Douglas GA": ("out", """
Gray's Septic Service|(912) 592-1184|5.0|w
A & C Septic Tanks & Portable Toilets|(912) 383-7005|4.8|w
Down Under Enterprises|(912) 384-2487|4.2|-
Clement Septic Tank|(229) 425-7926|5.0|w
Veterans Drain Solutions|(912) 327-0128||w
Mr. Rooter Plumbing of SE Georgia|(912) 623-4240|4.8|w
"""),
 "Valdosta GA": ("out", """
Herring Septic Service|(229) 356-1786|4.8|w
Checkered Flag Septic Service|(229) 559-0331|4.4|-
Septic Tank Pros Valdosta|(229) 415-7780|3.7|w
Hunter Plumbing & Septic|(229) 292-8625|5.0|-
Best Way Septic Service|(229) 563-2778|4.2|w
aHunter Septic Tank Service|(229) 292-8625|4.5|-
H&H Drain Cleaning|(229) 292-8625|4.9|-
"""),
 "Jacksonville NC": ("out", """
Ray's Septic Service|(910) 347-7867|4.6|w
Royal Flush Septic Services|(910) 546-2092|5.0|w
G & G Pumping|(910) 915-9322|4.9|w
Septic Solutions Jacksonville|(910) 358-2888|5.0|w
Fisher Septic & Excavation|(910) 358-0820|4.8|-
Plowboy Septic|(910) 346-8904|4.7|w
Atlantic All-Pro Septic Tank|(910) 346-3995|4.0|-
"""),
 "Morehead City NC": ("out", """
Rouses Septic Tank Services|(252) 726-6761|4.4|-
R & W Septic Tank Services|(252) 726-7390|4.6|-
All County Septic|(252) 241-4929|4.7|w
Carteret Septic Tank & Construction|(252) 241-1748|4.7|w
Ballou & Sons Construction|(252) 726-2138||-
Garner Construction Co|(252) 223-4019|3.9|-
"""),
 "Wilmington NC": ("out", """
Skipper Septic Tank Service|(910) 791-9488|4.5|w
Dan Inman Septic Tank|(910) 763-1146|4.1|w
Wilmington Septic Tank Service|(910) 541-8727|3.7|w
The Sewer & Drain Medic|(910) 233-9618|4.9|w
Septic Services in Wilmington|(910) 984-2233||w
Lewis Farms & Liquid Waste|(910) 283-9823|4.9|w
Clark's Septic and Land Services|(910) 549-8124|5.0|w
"""),
 "Charleston SC": ("out", """
A-1 Septic Tank Service|(843) 766-4464|3.6|w
Knights Septic Tank Services|(843) 747-0737|4.7|w
Superior Charleston Septic|(843) 806-0001|5.0|-
Island Septic Systems|(843) 559-3491|4.9|w
Fain Septic Tank Services|(843) 553-0888|4.0|-
Charleston Septic Tank Pumping|(843) 547-2079||-
"""),
 "Myrtle Beach SC": ("out", """
Elvis Service Company|(843) 448-5016|4.8|w
Quick Fix Septic|(843) 631-2332||w
"""),
},

"well pump repair": {
 "Jacksonville FL": ("core", """
Affordable Well Pump Services|(904) 365-7995|4.8|w
Well Dr & Accessories|(904) 999-9975|4.7|w
American Well & Irrigation|(904) 249-5400|4.7|w
Partridge Well Drilling|(904) 269-1333|4.8|w
Florida Pump Service|(904) 269-0202|4.6|w
Destin's Well & Pump Services|(904) 209-8866|4.2|-
Hulihan Territory Outdoor Solutions|(904) 773-4867|4.9|w
Williams Well Drilling|(904) 241-8489|5.0|-
Complete Services Water Well|(904) 693-8635|4.6|w
Englewood Well & Pump|(904) 724-3145|4.1|-
Riverview Pump Well & Septic|(904) 764-4568|4.2|w
Blue Spring Well and Pump|(904) 412-4822|4.8|w
"""),
 "Jacksonville Beach FL": ("core", """
American Well & Irrigation|(904) 249-5400|4.7|w
Owens & Sons Plumbing|(904) 590-7600|4.8|w
Hulihan Territory Outdoor Solutions|(904) 773-4867|4.9|w
Destin's Well & Pump Services|(904) 209-8866|4.2|-
Affordable Well Pump Services|(904) 365-7995|4.8|w
Williams Well Drilling|(904) 241-8489|5.0|-
Well Dr & Accessories|(904) 999-9975|4.7|w
"""),
 "Orange Park FL": ("core", """
Affordable Well Pump Services|(904) 365-7995|4.8|w
Florida Pump Service|(904) 269-0202|4.6|w
"""),
 "Fleming Island FL": ("core", """
Affordable Well Pump Services|(904) 365-7995|4.8|w
Florida Pump Service|(904) 269-0202|4.6|w
Partridge Well Drilling|(904) 269-1333|4.8|w
Well Dr & Accessories|(904) 999-9975|4.7|w
Smitty's Pump Services|(904) 282-7318|5.0|-
Daymon Well Drilling & Pump|(904) 282-1121|4.7|w
Advanced Pump Service|(904) 203-7468|4.5|w
"""),
 "Saint Johns FL": ("core", """
Well Dr & Accessories|(904) 999-9975|4.7|w
Affordable Well Pump Services|(904) 365-7995|4.8|w
Partridge Well Drilling|(904) 269-1333|4.8|w
Superior Well and Pump Service|-|4.6|-
Destin's Well & Pump Services|(904) 209-8866|4.2|-
Florida Pump Service|(904) 269-0202|4.6|w
St. Johns Well & Pump Service|(904) 239-7703|5.0|-
"""),
 "Nocatee FL": ("core", """
Well Dr & Accessories|(904) 999-9975|4.7|w
Affordable Well Pump Services|(904) 365-7995|4.8|w
Partridge Well Drilling|(904) 269-1333|4.8|w
Superior Well and Pump Service|-|4.6|-
Destin's Well & Pump Services|(904) 209-8866|4.2|-
St. Johns Well & Pump Service|(904) 239-7703|5.0|-
Aqua 1 Well & Pump|(904) 829-2837|4.5|w
"""),
 "Callahan FL": ("fringe", """
Mumford & Son Well Drilling|(904) 879-2870|5.0|-
Mizell Well & Pump|(904) 879-6871|4.8|-
David Weeks Well & Pump|(904) 268-6907|4.8|-
Advanced Well Drilling & Water|(912) 414-1278|4.5|w
The Pump Guy|(904) 727-8976|5.0|-
Affordable Well Pump Services|(904) 365-7995|4.8|w
"""),
 "Macclenny FL": ("fringe", """
Martin Well Drilling|(904) 259-9014|3.2|-
Ronnie Sapp Well Drilling|(904) 259-6934|3.1|-
Smitty's Pump Services|(904) 282-7318|5.0|-
Affordable Well Pump Services|(904) 365-7995|4.8|w
Sapp Plumbing and Drilling|(904) 259-6934|3.0|-
Drains Plus of Jacksonville|(904) 510-7358|4.9|-
"""),
 "Green Cove Springs FL": ("fringe", """
Affordable Well Pump Services|(904) 365-7995|4.8|w
Daymon Well Drilling & Pump|(904) 282-1121|4.7|w
Smitty's Pump Services|(904) 282-7318|5.0|-
Clay Pump & Industrial Supplies|(904) 284-4879|5.0|-
Advanced Pump Service|(904) 203-7468|4.5|w
Florida Pump Service|(904) 269-0202|4.6|w
Well Dr & Accessories|(904) 999-9975|4.7|w
"""),
 "Saint Augustine FL": ("core", """
Aqua 1 Well & Pump|(904) 829-2837|4.5|w
East Coast Wells & Water Treatment|(904) 824-6630|4.7|w
St. Johns Well & Pump Service|(904) 239-7703|5.0|-
St Augustine Electric Motor Works|(904) 829-8211|4.8|w
b & m wells, pumps, water treatment|(904) 466-7498||-
Southland Well Drilling|(904) 824-0774|5.0|-
"""),
 "Yulee FL": ("fringe", """
Advanced Well Drilling & Water|(912) 414-1278|4.5|w
Mumford & Son Well Drilling|(904) 879-2870|5.0|-
Mizell Well & Pump|(904) 879-6871|4.8|-
NE Florida Well & Pump|(904) 753-1367|4.8|w
Affordable Well Pump Services|(904) 365-7995|4.8|w
Destin's Well & Pump Services|(904) 209-8866|4.2|-
"""),
 "Fernandina Beach FL": ("fringe", """
NE Florida Well & Pump|(904) 753-1367|4.8|w
Destin's Well & Pump Services|(904) 209-8866|4.2|-
Mumford & Son Well Drilling|(904) 879-2870|5.0|-
Advanced Well Drilling & Water|(912) 414-1278|4.5|w
American Well & Irrigation|(904) 249-5400|4.7|w
Dustin Turner Plumbing|(904) 817-9508|5.0|w
Superior Well and Pump Service|-|4.6|-
"""),
 "Starke FL": ("out", """
Durrance Pump & Supply|(904) 964-7061|4.3|-
Smitty's Pump Services|(904) 282-7318|5.0|-
Dykes Pump Service|(352) 473-0348|5.0|-
North Fla Well Drilling & Pump|(352) 473-3204|4.7|w
Affordable Well Pump Services|(904) 365-7995|4.8|w
Bronco Well Drilling|(352) 473-0534|4.7|w
Daymon Well Drilling & Pump|(904) 282-1121|4.7|w
"""),
 "Keystone Heights FL": ("out", """
Dykes Pump Service|(352) 473-0348|5.0|-
North Fla Well Drilling & Pump|(352) 473-3204|4.7|w
Bronco Well Drilling|(352) 473-0534|4.7|w
After Hours Well & Pump|(352) 358-7420|5.0|-
Durrance Pump & Supply|(904) 964-7061|4.3|-
Smitty's Pump Services|(904) 282-7318|5.0|-
Affordable Well Pump Services|(904) 365-7995|4.8|w
"""),
 "Hawthorne FL": ("out", """
After Hours Well & Pump|(352) 358-7420|5.0|-
Perry - Pump Repair Service|(352) 320-2412|4.9|w
Lucky's Pump Service|(352) 481-2883|4.6|-
Archer Pump Service|(352) 495-2024|4.9|w
Boyette Pump and Well Service|(813) 923-0008|5.0|w
Durrance Pump & Supply|(904) 964-7061|4.3|-
Burch Well & Pump|(352) 466-3485|5.0|w
"""),
 "Gainesville FL": ("out", """
Perry - Pump Repair Service|(352) 320-2412|4.9|w
A & W Pump Service|(352) 575-8818|4.9|w
Dampier Well and Pump Service|(352) 275-6553|5.0|w
Perry's Pump Repair|(352) 316-4088|4.9|w
All County Water|(352) 514-3745|4.9|w
Archer Pump Service|(352) 495-2024|4.9|w
Burch Well & Pump|(352) 466-3485|5.0|w
"""),
 "Ocala FL": ("out", """
Bryant's Pump Service & Well Drilling|(352) 900-5839|4.7|w
Smokey's Pump Service|(352) 732-5570|4.9|w
WaterBoys Emergency Well Repair|(352) 977-9355|5.0|w
Ocala Well and Septic|(352) 425-7161|4.9|-
Advanced Well Drilling|(352) 723-0123|5.0|w
Sweetwater Well Drilling & Pump|(352) 402-9355|4.6|w
B & C Enterprises Well Drilling|(352) 629-1098|4.9|w
"""),
 "Lake City FL": ("out", """
Hall's Pump & Well Services|(386) 752-1854|4.5|w
Lynch Well Drilling|(386) 288-5975|4.8|w
Fargo Well & Pump Services|(386) 752-3039|5.0|-
A&B Well Drilling & Pump|(386) 999-4827|4.9|w
Jupiter Pump and Well|(561) 747-4770|5.0|-
WaterBoy Well Repair and Drilling|(386) 330-6099|4.5|-
Hingson's Pump & Water Solutions|(386) 364-8128|5.0|-
"""),
 "Tallahassee FL": ("out", """
KCW Water Well Service|(850) 510-6887|4.8|w
Mills Well Drilling|(850) 562-2906|4.5|w
C & L Well & Pump Services|(850) 570-9153|4.9|w
Robin Dean Well Drilling|(850) 421-7203|4.5|w
Capital Well & Pump|(850) 894-4439|4.7|w
Simmons Well Service and Repair|(850) 878-8489|5.0|w
"""),
 "Brunswick GA": ("out", """
Woodrow Sapp Well Drilling|(912) 265-2603|4.5|w
Coastal Pump Service|(912) 264-2048|4.8|w
Golden Isles Well Drilling|(912) 264-1133|4.6|-
Cox Well Drilling & Pump Service|(912) 258-2642|5.0|w
"""),
 "Saint Marys GA": ("out", """
JS Well Drilling Kingsland|(912) 504-4204|5.0|-
O'Quinn Well Drilling|(912) 729-7800|4.8|-
Advanced Well Drilling & Water|(912) 414-1278|3.5|-
Cox Well Drilling|(912) 552-3308||-
Cox Well Drilling & Pump Service|(912) 258-2642|5.0|w
NE Florida Well & Pump|(904) 753-1367|4.8|w
Affordable Well Pump Services|(904) 365-7995|4.8|w
"""),
 "Waycross GA": ("out", """
Thrift Well Drilling|(912) 285-8874|4.6|-
Goulds Pumps|(912) 285-2524|4.3|-
Mock Drilling Co|(912) 283-0530|2.7|-
Middleton Drilling Co|(912) 462-3507|4.9|-
Cox Well Drilling & Pump Service|(912) 258-2642|5.0|w
Brown Well Drilling & Pump|(912) 367-6225|4.9|w
"""),
 "Douglas GA": ("out", """
Pittman Pump & Well Drilling|(912) 422-3484|4.9|-
Miller Pump & Electric|(912) 384-3209|4.1|-
"""),
 "Valdosta GA": ("out", """
Valdosta Well and Pump|(229) 896-4403|4.0|w
Creasy Well Drilling Co|(229) 244-0558|3.8|-
Paulk's Well Drilling|(229) 244-5296|3.0|-
Everetts Well Drilling & Service|(229) 263-4192|4.8|w
Aqua Logistics Well Drilling|(229) 559-8272|5.0|w
A W Stubbs Well Service|(229) 292-2235|5.0|-
Flythe's Well & Pump Services|(229) 242-2617|3.0|-
"""),
 "Jacksonville NC": ("out", """
Wild Water Plumbing + Septic|(910) 750-2312|4.9|w
Superior Well and Pump Service|-|4.6|-
Riverview Pump Well & Septic|(904) 764-4568|4.2|w
Coastal Geothermal|(910) 353-0926|4.5|w
Blue Spring Well and Pump|(904) 412-4822|4.8|w
Meadows Well Drilling|(910) 619-1076|4.6|-
"""),
 "Morehead City NC": ("out", """
Aqua Well & Pump Services|(252) 728-7867|4.6|w
Morton Well Drilling|(252) 222-0513|3.7|w
Anderson Priority Service|(252) 240-2771|4.9|w
"""),
 "Wilmington NC": ("out", """
Sage Drilling & Pump Services|(910) 231-6669|4.9|w
TWS Well Service & Water Systems|(910) 679-6101|5.0|-
Craig's Well Drilling & Pump|(910) 799-9604||w
Coastal Well & Pump|-|4.0|-
Skipper's Well Drilling & Pump|(910) 371-2770|4.4|w
Aqua Well Drilling (Shallow)|(910) 395-1987|4.5|-
"""),
 "Charleston SC": ("out", """
J P Anderson Well & Pump|(843) 810-4045|4.8|w
Anderson Well Drilling|(843) 889-8144|4.1|-
H.M. Northcutt Corporation|(843) 884-4952|5.0|w
Affordable Well Drilling|(843) 714-4570|4.5|-
"""),
 "Myrtle Beach SC": ("out", """
Mike Welch Well Drilling|(843) 340-0283|4.8|w
Hodge Well Drilling & Pump|(843) 756-3843|3.8|-
Jesse's Well Pump & Filtration|(803) 585-9001|4.9|w
Horry's Water Well|(843) 726-8560|4.9|w
Cribbs Well Drilling|(843) 340-4340|4.2|-
B & B Well Drilling|(843) 765-4059|4.9|w
Southlantic Services|(843) 626-9856|4.9|w
"""),
},

"boat detailing": {
 "Jacksonville FL": ("core", """
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
Coastal Boat Detailing|(904) 451-7455|5.0|w
Florida Marine Detailing|(904) 614-7560|5.0|w
Dockside Mobile Marine|(904) 716-3966|5.0|w
Moran's Performance Detailing (car)|(904) 717-7127|5.0|w
Salty Boat Worx|(904) 667-8312|5.0|-
"""),
 "Jacksonville Beach FL": ("core", """
Jacksonville Beach Local Pool Cleaners (n/a)|-|-|-
"""),
 "Ponte Vedra Beach FL": ("core", """
Florida Marine Detailing|(904) 614-7560|5.0|w
Speedy Mobile Car Detailing (car)|(904) 736-6521|5.0|w
Pristine Mobile Car Detailing (car)|(904) 872-7679|5.0|w
Coastal Boat Detailing|(904) 451-7455|5.0|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
Ponte Vedra Mobile Detailing (car)|(904) 534-6464|5.0|w
"""),
 "Fleming Island FL": ("core", """
VH Auto and Marine Detailing|(904) 465-4896|5.0|-
Island Cove Detailing Co|(904) 600-4499|5.0|w
Coastal Boat Detailing|(904) 451-7455|5.0|w
Anchors Up Marine Detailing & Gelcoat|(904) 200-7703|4.6|w
B&T Mobile Auto Detailing (car)|(904) 235-6419|5.0|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
"""),
 "Orange Park FL": ("core", """
B&T Mobile Auto Detailing (car)|(904) 235-6419|5.0|w
Clean&Shine Mobile Detailing (car)|(904) 579-3713|4.8|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
Waxman Mobile CarWash (car)|(904) 780-5548|4.8|w
Coastal Boat Detailing|(904) 451-7455|5.0|w
Excel Professional Detailing & Fiberglass|(904) 716-2803|5.0|w
"""),
 "Middleburg FL": ("fringe", """
Anchors Up Marine Detailing & Gelcoat|(904) 200-7703|4.6|w
Coastal Boat Detailing|(904) 451-7455|5.0|w
Island Cove Detailing Co|(904) 600-4499|5.0|w
Blue Water Boat Detailing (mobile)|(904) 444-3757|5.0|-
"""),
 "Nocatee FL": ("core", """
Florida Marine Detailing|(904) 614-7560|5.0|w
Next Level Auto Solutions (car)|-|5.0|-
Coastal Boat Detailing|(904) 451-7455|5.0|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
Mavinate Boat Detailing & Restoration|(386) 566-6483|5.0|w
All Pro Auto Detailing (car)|(240) 988-1401|5.0|w
"""),
 "Saint Augustine FL": ("core", """
Top Knotch Marine Detailing|(904) 315-5130|5.0|-
St Augustine Boat Works Decks Docks Detailing|(321) 372-4294|5.0|w
West Shore Boat Detailing|(813) 390-0119||-
North Florida Yacht Services & Marine Detailing|(904) 557-1994|5.0|w
SunCoast Boat Detailing|(904) 274-3156|5.0|w
St Augustine Detailing and Reconditioning (car)|(904) 315-2603|4.8|w
Detail One (car)|(904) 826-9123|5.0|w
"""),
 "Amelia Island FL": ("fringe", """
Salt & Suds|(360) 688-4705|5.0|-
Coastal Boat Detailing|(904) 451-7455|5.0|w
Moran's Performance Detailing (car)|(904) 717-7127|5.0|w
The Waters' Edge Complete Boat Detailing|(904) 571-0725|5.0|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
KaTuna's Marine Detailing|(904) 629-6565|5.0|-
Chelsea Boat Center|(904) 261-8884|4.7|w
"""),
 "Yulee FL": ("fringe", """
Coastal Boat Detailing|(904) 451-7455|5.0|w
Salt & Suds|(360) 688-4705|5.0|-
Bo & Mike's Detail Shop (car)|(904) 261-4642|4.5|-
Moran's Performance Detailing (car)|(904) 717-7127|5.0|w
Florida Marine Detailing|(904) 614-7560|5.0|w
WE DETAIL Mobile Car Detailing (car)|(904) 339-6371|4.8|w
"""),
 "Callahan FL": ("fringe", """
Florida Marine Detailing|(904) 614-7560|5.0|w
Renewed Reflections Detailing CD|(904) 580-4344|5.0|w
Moran's Performance Detailing (car)|(904) 717-7127|5.0|w
Nautical Shine Florida|(904) 728-2358|5.0|w
Royalte Detailing|(904) 898-8851||w
Mavinate Boat Detailing & Restoration|(386) 566-6483|5.0|w
Excel Professional Detailing & Fiberglass|(904) 716-2803|5.0|w
"""),
 "Macclenny FL": ("fringe", """
Florida Marine Detailing|(904) 614-7560|5.0|w
D's auto detailing (car)|(904) 910-1458||-
Coastal Boat Detailing|(904) 451-7455|5.0|w
Jacksonville Mobile Boat Detailing|(904) 465-6312|5.0|w
Moran's Performance Detailing (car)|(904) 717-7127|5.0|w
Kaleb's Mobile Detailing (car)|(904) 408-2792|5.0|w
"""),
 "Gainesville FL": ("out", """
Spartan Mobile Detailing RVs and Boats|(352) 870-9282|4.7|w
Express Detailing Mobile|(352) 450-6080|4.9|w
Kingdom Builders Smart Repairs|(352) 871-2454|4.9|w
NextGen Auto Spa (car)|(352) 224-9135|5.0|w
Gator Wash & Detail (car)|(352) 562-9877|5.0|w
Stanley Detailing (car)|(352) 284-6313|5.0|-
Integrity Marine Detail|(352) 318-8900|5.0|w
"""),
 "Ocala FL": ("out", """
Ocala Detailing: Auto, RV, Equipment|(352) 547-5206|5.0|w
Performance Mobile Detail|(352) 829-9037|4.9|w
Pristine Detailing Ocala|(352) 209-7371|5.0|w
All Detailz|(352) 362-6142|5.0|-
K-BACH Detailing|(352) 673-3687|5.0|-
TLC Luxury Detailing|(352) 648-0191|5.0|w
VIP Car Details Studio|(352) 361-8677|4.9|w
"""),
 "Lake City FL": ("out", """
Lake City Mobile Detailing|(386) 292-6690|4.9|w
Mikes Auto & Marine|(386) 288-3651|4.8|-
Truck Wash Carwash and Detailing|(386) 292-4765|4.9|-
North Florida Marine|(386) 697-1637|5.0|w
Registers Mobile Auto Detailing|(386) 466-5400|4.7|-
Sheppards Prosperity Auto Detailing|(386) 466-9305|4.3|-
Florida Boat Detailing|(386) 214-0667|4.9|w
"""),
 "Starke FL": ("out", """
Ray Ray's Detailing|(904) 364-7889|4.9|-
Stanley Detailing|(352) 284-6313|5.0|-
Danielle's Auto Salon|(904) 454-0790|4.9|w
Anchors Up Marine Detailing|(904) 200-7703|4.6|w
JC Auto Detailing|-||-
Jayla's Detailing|(352) 231-6044||-
Blue Water Boat Detailing (mobile)|(904) 444-3757|5.0|-
"""),
 "Tallahassee FL": ("out", """
Tally's Panhandle Detail|(850) 228-9932|4.9|w
Dan's Car Detailing|(561) 403-7414|5.0|w
AUTO DETAILS by Custom Detailing|(850) 339-1269|5.0|w
Excelente Mobile Detailing|(850) 321-4796|5.0|w
Top Gunn Detailing|-|5.0|w
Ultimate Auto Detailing|(850) 559-3712|5.0|w
Mob Car Detailing of Tallahassee|(240) 584-0572|5.0|w
"""),
 "Brunswick GA": ("out", """
Brunswick Landing Boat Yard|(912) 275-7373|4.6|w
Navcom Marine Services|(912) 242-2192|5.0|w
Elite Detailing (car)|(912) 242-4070|5.0|-
Mike's Auto Spa (car)|(912) 571-7166|4.5|w
1st Class Mobile Automotive Detailing|(912) 328-7854|5.0|w
Mariner Marine Services|(912) 230-8703|4.5|w
Ricio's Mobile Auto Detailing|(912) 571-9218|5.0|w
"""),
 "Saint Marys GA": ("out", """
Over The Top Detailing|(912) 322-0467|4.9|w
Waxing Moon Detailing|(912) 676-7648|5.0|w
St Marys Boat Services|(912) 540-0640|4.6|w
Captain Tommy's Marine Service|(912) 464-2661|4.0|-
ChonkoAutoWorks|(912) 464-9031|5.0|w
Insetta Boatworks|(912) 882-5420|4.4|w
Premier Mobile Services|(956) 755-9747|4.9|-
"""),
 "Waycross GA": ("out", """
Satilla Marine|(912) 285-8115|4.6|w
Manders Mobile Detailing|(912) 614-4292|5.0|-
Wallis Mobile Marine Detailing|(404) 561-9106|5.0|w
T-N-T Mobile Car Wash|(912) 387-1589|4.7|-
MT. Rich Mobile Detailing|(912) 387-6806|4.8|-
Method Auto Detailing|(912) 452-0667|5.0|w
"""),
 "Douglas GA": ("out", """
Southeastern Marine and Repair|(912) 384-7244|3.9|w
Lott Marine|(912) 384-2299|4.5|w
Simply Clean AutoSpa (car)|(912) 388-9126|5.0|w
Marine Concepts Detailing (GA)|(678) 283-4349|4.7|w
Marine Klean & Auto Klean (GA)|(770) 925-5326|4.9|w
Brown's Boat Detailing (GA)|(678) 296-2957|4.2|w
"""),
 "Valdosta GA": ("out", """
Preferred Auto Detailing Valdosta|(229) 454-0534|4.7|w
Green Diamond Mobile Detailing|(229) 632-6038|4.8|w
Las Banderas Car Wash & Detail|(229) 600-4570|4.3|w
Cason's Mobile Detailing|(229) 531-8212|4.8|-
Otto Detailing|(229) 403-4548|5.0|w
Mcconnehead Car Wash & Detail|(229) 444-9500|4.7|w
First Line Mobile Detailing|(229) 531-3843|5.0|w
"""),
 "Morehead City NC": ("out", """
Marine Detail Supply Company|(252) 723-9523|5.0|w
All In One Yacht Maintenance|(252) 725-4952|4.5|w
Fish On Mobile Marine Service & Detailing|(252) 648-2591|5.0|w
At The Dock Detailing|(252) 732-0725|5.0|-
Will's Marine Detailing|(252) 515-0203|5.0|w
Bow 2 Bumper Detailing|(252) 999-0203|5.0|w
Marine Detail Professionals|(919) 761-4381|5.0|w
"""),
 "Wilmington NC": ("out", """
Attention2details boat detailing|(910) 520-2919|5.0|w
J&J Boat Services|(910) 679-9844|5.0|w
First Choice Boat Detailing|(910) 617-2152|5.0|w
Seagate Marine Detailing|(910) 859-1129|5.0|-
Cape Fear Marine Detailing|(910) 541-3329|5.0|w
Carolina Coastal Detail|(910) 809-2628|5.0|w
Carolina Coastal Marine|(910) 809-2628|5.0|w
"""),
 "Jacksonville NC": ("out", """
Chandler's Detailing|(540) 451-1998|5.0|w
James International Services Detailing|(919) 903-1450|4.9|w
Heather's Boat Detailing|(252) 342-1958|4.8|w
"""),
 "Myrtle Beach SC": ("out", """
Attention to Detail Myrtle Beach|(843) 591-8420|4.7|w
Attention To Detail Auto & Marine|(843) 427-0069|5.0|w
Pristine Shine Auto Spa|(843) 504-6913|5.0|w
Boats & Hoses Detailing|(843) 780-1141|4.9|-
Dun-Rite Detailing|(843) 318-9843|5.0|w
Rapid Shine Detailing|(843) 450-2902|4.9|-
Ceramic Pro of Myrtle Beach|(843) 267-0953|4.9|w
"""),
 "Charleston SC": ("out", """
__pending__|-|-|-
"""),
},
}

# Dock / marine construction, hurricane shutters, porta potty, generators, land clearing:
# captured as market-level counts (operator lists existed but were long and repetitive);
# kept here as aggregates so the record is complete without inventing rows.
AGG = [
 # service, metro, region, operators, median_rating, no_website, note
 ("dock / marine construction","Jacksonville FL","core",10,4.85,2,"B&W, Barefoot, Kenyon, Serenity, Top Dog, Cove Points, Coastal Marine, Dock Doctors, Ashcraft, Master Marine"),
 ("dock / marine construction","Jacksonville Beach FL","core",9,4.8,1,"same metro pool + Docks, Decks & More, Legacy, Tidewater"),
 ("dock / marine construction","Ponte Vedra Beach FL","core",8,4.9,0,"OutBack, Docks Decks, Elite, Barefoot, Master Marine, Serenity, Coastal Marine"),
 ("dock / marine construction","Saint Johns FL","core",8,5.0,1,"Dock On!, Coastal Marine, Anchor Marine(3.0), Ashcraft, Master Marine, Top Dog, Dock Doctors"),
 ("dock / marine construction","Nocatee FL","core",7,5.0,0,"OutBack, Coastal Marine, Master Marine, Docks Decks, Ashcraft, Dock Doctors, Barefoot"),
 ("dock / marine construction","Fleming Island FL","core",8,5.0,0,"Dock Experts, Legacy, Top Dog, Coastal Marine, Dock On!, Brothers Marine, Creekside"),
 ("dock / marine construction","Middleburg FL","core",7,4.9,0,"Dock Experts, Top Dog, Legacy x2, Creekside, Legacy Docks, Kenyon"),
 ("dock / marine construction","Green Cove Springs FL","fringe",7,4.6,1,"Marine CS(4.0,nosite), Top Dog, Creekside, Green Cove Marina, Black Creek Marina, McKinney Marine, Dock Experts"),
 ("dock / marine construction","Saint Augustine FL","fringe",7,4.85,2,"Olde Florida, St Aug Boat Works, LaConte(nosite), Yelton, Miner's(nosite), Oasis Boat Yard, Right Price(nosite)"),
 ("dock / marine construction","Callahan FL","fringe",7,4.9,1,"Kenyon, Cove Points, Pickett(nosite), Serenity, Coastal Marine, Tidewater(nosite), Barefoot"),
 ("dock / marine construction","Macclenny FL","fringe",7,4.9,1,"Kenyon, Top Dog, Legacy Docks, Legacy, Cove Points, Serenity, Tidewater"),
 ("dock / marine construction","Brunswick GA","out",3,4.8,0,"Marineco, Brunswick Landing Boat Yard, Atlas Marine"),
 ("dock / marine construction","Saint Marys GA","out",2,4.6,1,"St Marys Boat Services, Pierce Marine(nosite)"),
 ("dock / marine construction","Morehead City NC","out",7,5.0,1,"Outer Banks Marine, Buck(nosite), inner banks, Edgewater, Carteret Marine, Dynamic East, EZ Dock"),
 ("dock / marine construction","Wilmington NC","out",7,5.0,0,"North End, Dock Doctors, Vision, Wilmington Marine, F&S Lift Pro, F and S Marine, Logan Marine"),
 ("dock / marine construction","Myrtle Beach SC","out",7,5.0,0,"MB Elite, Greenbeach, Waterbridge, Myers, Beaver, Seven Seas(3.4), Dock Dudes"),
 ("dock / marine construction","Ocala FL","out",7,4.9,1,"Type1(nosite), JSC, Florida Docks, American Marine, Trailer Doc, Florida Dock & Boat Lifts, Millers"),
 ("hurricane shutter installation","Jacksonville FL","core",7,5.0,0,"First Coast Hurricane Shutters + 6 window-treatment/installation firms; only 1 true shutter specialist"),
 ("hurricane shutter installation","Jacksonville Beach FL","core",7,5.0,0,"same pool + Beach Shutters and Blinds, NAC Installs"),
 ("hurricane shutter installation","Ponte Vedra Beach FL","core",7,5.0,0,"First Coast, NAC, Mastercraft, Beach Shutters, Budget Blinds, KMS, Reece"),
 ("hurricane shutter installation","Orange Park FL","core",2,5.0,1,"First Coast Hurricane Shutters, Hurricane Protection by Design (nosite) - thinnest core cell"),
 ("hurricane shutter installation","Middleburg FL","core",7,4.9,1,"First Coast, Window World, Better Exterior, Reece, Anderson, ArmorGuard, Hurricane Protection by Design(nosite) - mostly generic"),
 ("hurricane shutter installation","Green Cove Springs FL","fringe",5,5.0,0,"First Coast, Hurricane Armor, Smart Guard(4.9), Better Exterior, APS Hurricane(4.8)"),
 ("hurricane shutter installation","Saint Johns FL","fringe",7,5.0,0,"First Coast, Mastercraft, Window World, Titan, Those Blind Guys, Budget Blinds, All About Blinds"),
 ("hurricane shutter installation","Fleming Island FL","fringe",7,5.0,0,"First Coast, Hurricane Protection by Design, Window World, Reece, Renewal by Andersen, Better Exterior, Action Windows"),
 ("hurricane shutter installation","Saint Augustine FL","fringe",5,5.0,0,"Titan(4.1), Anastasia Shutters, First Coast, Waters Edge, Gotcha Covered"),
 ("hurricane shutter installation","Callahan FL","fringe",7,5.0,1,"First Coast, J Rowland, NAC, Wells Windows(nosite,no rating), Mastercraft, Reece, Hurricane Protection by Design"),
 ("hurricane shutter installation","Yulee FL","fringe",7,5.0,0,"J Rowland, First Coast, Bayside Shades, Mastercraft, Reece, NAC, Wyatt's(4.9)"),
 ("hurricane shutter installation","Fernandina Beach FL","fringe",5,5.0,0,"Bayside Shades, J Rowland, First Coast, NAC, Reece"),
 ("hurricane shutter installation","Gainesville FL","out",5,4.9,0,"72 Hour Blind Factory, Gotcha Covered, Budget Blinds, My Blind and Shutter Store, First Coast (no local shutter specialist)"),
 ("hurricane shutter installation","Ocala FL","out",7,4.9,0,"Arnold's Aluminum, Gator Blinds, Grand View, Budget Blinds, Windoor, CWS(3.1), RC Windows"),
 ("hurricane shutter installation","Lake City FL","out",5,4.9,0,"Advanced Sun Shade, Florida Hurricane Shutters, Hurricane Shutter 4u, United Hurricane, Total Hurricane - all out-of-area phone numbers"),
 ("hurricane shutter installation","Tallahassee FL","out",7,5.0,0,"Made in the Shade, Budget Blinds, Gulf Breeze, NRG, Florida Window Coverings, JM Storm Shutter, MPC"),
 ("hurricane shutter installation","Brunswick GA","out",5,4.9,0,"Plantation Shutter Co(4.2), Little's Custom, Coastal Shutters, Palmetto, Garage Door of Brunswick"),
 ("hurricane shutter installation","Saint Marys GA","out",5,5.0,0,"Custom Built Aluminum, J Rowland, Budget Blinds Golden Isles, World Class Windows, Cleansafe"),
 ("hurricane shutter installation","Waycross GA","out",7,4.9,0,"Heritage Pro Coatings, Security Blanket, Southern Gutter x2, J&M, White Star, Plantation Shutter Co - no local shutter specialist"),
 ("hurricane shutter installation","Douglas GA","out",7,4.8,0,"Castleberry(5.0), Dubberly's Glass(4.4), RGC Roofs, Window World SGA, Lowe's, South Georgia Shutters(3.7), Prograde"),
 ("hurricane shutter installation","Valdosta GA","out",7,4.8,0,"Window World SGA, A Shade of Perfection(4.3), Plantation Shutter & Blind, Fisher Rain Gutter, Hector & Sons, HC Wilkinson, Southern Window Works"),
 ("hurricane shutter installation","Wilmington NC","out",5,4.9,0,"Port City, American Hurricane, Seacoast Systems, Creative Outdoor, Wilmington Awning"),
 ("hurricane shutter installation","Morehead City NC","out",4,4.6,0,"Atlantic Breeze(4.9), Coastal Awnings(4.3), Hurricane Shield Systems, Shutter Solutions - 2 of 4 unrated"),
 ("hurricane shutter installation","Charleston SC","out",5,4.9,0,"Lowcountry, Coastal Shutter, Windward, Carolina Shutter & Blinds, Sea Island"),
 ("hurricane shutter installation","Myrtle Beach SC","out",5,4.9,0,"AAA Blind & Shutter, Midatlantic Storm Protection, Plantation Shutter Pros, Shade and Shutter Expo, Hurricane Shutters of MB"),
 ("porta potty rental","Jacksonville FL","core",7,5.0,4,"Jax Beach PP, Porta Potty Rentals Jax Beach, Neptune Beach PP, Floaters(4.5), Fortis, Porta Potty Rental Jax, Jax PP Rentals - most unrated/nosite"),
 ("porta potty rental","Jacksonville Beach FL","core",7,5.0,4,"Jax Beach PP(nosite), Porta Potty Rentals Jax Beach(nosite), Neptune Beach(nosite), Floaters, Fortis, Jax PP(nosite), Maxline"),
 ("porta potty rental","Ponte Vedra Beach FL","core",3,5.0,3,"PVB PP, Jax Beach Portable Toilet, Jax Beach PP - all no website"),
 ("porta potty rental","Nocatee FL","core",7,5.0,4,"PVB, Neptune Beach, Jax Beach x2, PP Rentals Jax Beach, Fortis, Carefree"),
 ("porta potty rental","Orange Park FL","core",7,5.0,0,"Fortis, Premier Restroom, Maxline, BoldRiver, Mobile Thrones, Jax PP, Floaters"),
 ("porta potty rental","Fleming Island FL","core",7,5.0,1,"Fortis, Fruit Cove Dumpster & PP(nosite), Floaters, Premier, BoldRiver, OP Dumpster & PP(nosite), Maxline"),
 ("porta potty rental","Middleburg FL","core",7,5.0,1,"Portable Toilet Rentals Middleburg(nosite), KM & Sons, Fortis, Deep Branch, Jax Portables, BoldRiver, Maxline"),
 ("porta potty rental","Green Cove Springs FL","fringe",7,5.0,2,"Neptune Beach(nosite), Fortis, Floaters, Jax Beach(nosite), Maxline, Carefree, Portable Toilet Rentals Middleburg"),
 ("porta potty rental","Saint Johns FL","fringe",7,5.0,2,"Neptune Beach(nosite), Fortis, Floaters, Jax Beach(nosite), Carefree, Jax PP, Maxline"),
 ("porta potty rental","Saint Augustine FL","fringe",3,5.0,1,"Carefree, Doodie Calls, Elite PP of St Augustine(nosite, unrated)"),
 ("porta potty rental","Saint Augustine Beach FL","fringe",3,5.0,1,"Carefree, Doodie Calls, Elite PP St Augustine(nosite)"),
 ("porta potty rental","Yulee FL","fringe",7,5.0,2,"Floaters, Neptune Beach, Fortis, Jax PP, PP Rental Jax, St Marys PP(nosite), Jax Beach PP"),
 ("porta potty rental","Fernandina Beach FL","fringe",7,5.0,3,"Jax Beach PP, Floaters, ASAP Marketplace(3.1), Fortis, PP Rentals Jax Beach, Atlantic Beach PT(nosite), BoldRiver"),
 ("porta potty rental","Callahan FL","fringe",7,5.0,2,"Floaters, Fortis, Neptune Beach, Jax PP, PP Rental Jax, Premier, Jax Beach PP"),
 ("porta potty rental","Macclenny FL","fringe",7,5.0,2,"Premier, Floaters, Fortis, Jax Beach PP, Maxline, United Rentals(4.8), PP Rentals Jax City(nosite)"),
 ("porta potty rental","Keystone Heights FL","out",7,5.0,2,"Gainesville PP, Hunk, Carefree, Fortis, Jax Beach PP, Floaters, Princess Portable(4.6)"),
 ("porta potty rental","Hawthorne FL","out",7,5.0,2,"Hunk, PP Rentals Gainesville, Gainesville PP, Gainesville PP Rentals, PP Rentals of Gainesville, NextGen, Gainesville Portable"),
 ("porta potty rental","Starke FL","out",7,5.0,2,"Premier, PP Rentals of Gainesville, Hunk, Floaters, Portable Toilet Rentals Middleburg, Gainesville PP Rentals, Princess(4.6)"),
 ("porta potty rental","Gainesville FL","out",7,5.0,3,"Gainesville PP, Hunk, PP Rentals of Gainesville, Floaters, Gainesville PP Rentals x2, PP Rentals Gainesville"),
 ("porta potty rental","Ocala FL","out",7,5.0,4,"Ocala PP Rentals x2, PP Rentals of Ocala(3.7), PP Rentals Ocala, Ocala Portable Toilet, PP Rental Ocala x2"),
 ("porta potty rental","Lake City FL","out",7,5.0,1,"386 INC, Doodie Calls, Porta Serve, Jones Luxury, Florida Portable, United Rentals(4.8), Veolia"),
 ("porta potty rental","Tallahassee FL","out",5,5.0,3,"Tallahassee PP Rentals, Tallahassee PP Supplier, Doodie Calls x2, Tallahassee Portable Potty"),
 ("porta potty rental","Brunswick GA","out",4,5.0,2,"Brunswick PP Rentals, Brunswick PT Rentals, Prime Portable(nosite.. has site), Golden Isles Disposal(3.5)"),
 ("porta potty rental","Saint Marys GA","out",2,5.0,2,"St Marys Portable Toilet, St Marys PP - neither has a website"),
 ("porta potty rental","Waycross GA","out",3,4.8,1,"Waycross PP, Sammy's Septic(4.2), Lewis Portable Restrooms"),
 ("porta potty rental","Douglas GA","out",2,4.8,1,"Douglas PP(nosite), A&C Septic"),
 ("porta potty rental","Valdosta GA","out",6,5.0,4,"Valdosta PP, Eugene PP, PP Rental Valdosta, Advanced Portable, Valdosta Porta Pros, Valdosta PT Rentals"),
 ("porta potty rental","Jacksonville NC","out",7,5.0,0,"Wild Water, Royal Flush, G&G, Septic Solutions, Fisher, Plowboy, Atlantic All-Pro"),
 ("porta potty rental","Morehead City NC","out",2,5.0,1,"Havelock PP(nosite), Patriot Waste"),
 ("porta potty rental","Wilmington NC","out",6,5.0,3,"Wilmington PP(nosite), Oasis Restroom Trailers, Wilmington PT(nosite), ENC Restroom, Alfonzo(4.0,nosite), Rent-A-John"),
 ("porta potty rental","Myrtle Beach SC","out",7,5.0,4,"MB PP, Elvis(4.8), MB PT(nosite), NMB PP(nosite), NMB PT(nosite), Ricky's, Palmetto"),
 ("porta potty rental","Charleston SC","out",7,4.6,3,"United Site Services(2.7), Mightrex, Charleston PP, N Charleston PP(nosite), Access(3.5), Charleston PP Restrooms, PP Rentals N Charleston"),
 ("generator repair","Jacksonville FL","core",7,4.9,0,"Generator Supercenter, Ronnie's Repair, DCS Electrician, American Electrical, GenCo, My Emergency Power, ACF Industrial"),
 ("generator repair","Jacksonville Beach FL","core",5,4.9,0,"DCS, Generator Supercenter, Patriot Tool, Crawford Electric, Tenax"),
 ("generator repair","Orange Park FL","core",7,4.6,0,"Orange Park Small Eng, Generator Supercenter, My Emergency Power, Premier Power(4.1), ACF, Northern Tool, Ronnie's"),
 ("generator repair","Fleming Island FL","core",5,4.9,0,"My Emergency Power, Generator Supercenter, JL Power Systems, A-1 Tool, ACF"),
 ("generator repair","Saint Johns FL","core",5,4.8,0,"SJ Electrician, Generator Supercenter, My Emergency Power, Double A, Florida Generator Specialists"),
 ("generator repair","Saint Augustine FL","fringe",5,4.7,0,"St Aug Electric Motor Works, Florida Generator Specialists, Ag-Pro, Elkton Engine, Braddock's"),
 ("generator repair","Middleburg FL","fringe",7,4.5,0,"Middleburg Power Equipment(4.1), A-1 Tool(4.0), Nationwide Electric, Ag-Pro(4.1), Generator Supercenter, Black Creek Electrical, Gearhead"),
 ("land clearing","Jacksonville FL","core",8,5.0,1,"Tomlinson, Southeast Forest, Advantage Outdoors, Varner, Shaw's(4.1), Set Apart(nosite), Champs, Christopher Rice(4.4)"),
 ("land clearing","Orange Park FL","core",7,5.0,1,"Florida Land Clearing, Tree Pros, Giddens, J&M Land and Demo, Tomlinson, Set Apart(nosite), Black Creek"),
 ("land clearing","Middleburg FL","core",2,5.0,0,"Florida Land Clearing, Black Creek Land Clearing"),
 ("land clearing","Saint Augustine FL","fringe",7,4.9,1,"Ancient City(4.3,nosite), Hicks(4.0), Precision, Bug's Tree, Clarkson's(4.1), Clint's, W.C.H"),
 ("mobile mechanic","Jacksonville FL","core",7,4.8,1,"Simple Mobile Mechanic, RC Mobile, Q's(nosite), Jax Mobile Mechanics, Pedroso, Tevin's, McDermott"),
 ("mobile mechanic","Jacksonville Beach FL","core",7,4.8,3,"Jax Cruisers, Q's(nosite), Neps(3.0,nosite), Mayport(nosite,unrated), McDermott, Simple, Bunting(nosite)"),
 ("marine salvage / recovery","Jacksonville FL","core",7,4.0,2,"Sea Tow(4.0), Dixie Towing(3.5), Safe Harbor, Lewis Diving, Logan Diving, Statewide Recovery, St Johns Boat - no dedicated salvage operator"),
 ("marine salvage / recovery","Jacksonville Beach FL","core",7,4.5,0,"Lewis Diving, Beach Marine, Logan Diving, Boathouse Discount, Sailors Exchange, Jax Boat Sales, St Johns Boat"),
]

# Market-level verdicts. Hand-set from the scan, not computed - the numbers justify but do
# not decide them.
ASSESS = {
 "boat detailing": ("gap","Mobile-first work with no shop requirement; core-river metros (Fleming Island, Orange Park, Middleburg, Amelia, Yulee) are thin on boat-only operators while the beaches are saturated at 5.0. The visible supply in most core metros is car detailers with a boat line."),
 "well pump repair": ("gap","Deepest supply gap in the drivable ring. Orange Park returned 2 listings, Macclenny 3.0-3.2-rated shops, and a large share of core/fringe operators have no website at all (Destin's, Williams, Smitty's, Mumford, Mizell, The Pump Guy, St Johns Well). 24-hour flags are common, which reads as intake gap, not visibility gap."),
 "hurricane shutter installation": ("gap","One true specialist (First Coast Hurricane Shutters) serves the whole core; every other result is a blinds store or window installer. Orange Park: 2 results. Consultative sale, so the sellable product is qualified appointments, not intake."),
 "marine salvage / recovery": ("thin-gap","2-3 results per metro and no dedicated marine salvage operator in any scanned metro - only dive shops and tow services. Genuine availability gap, but storm-gated: a burst business, best run as the surge-brokering adjunct."),
 "septic tank pumping": ("saturated","7-11 operators per metro at 4.3-5.0, nearly all with websites. No visibility gap anywhere in the ring. Only the after-hours intake angle survives."),
 "dock / marine construction": ("saturated","7-10 per metro, median 4.9-5.0, websites near-universal. Premium trade with established relationships; not a lead-gen opening."),
 "porta potty rental": ("saturated-but-sloppy","Heavy listing density, but a large share are unrated, no-website, city-name shell listings - the SEO-spam pattern. Real operators (Floaters, Premier, Fortis, Maxline, Carefree) are established. Not a clean gap."),
 "generator repair": ("adequate","5-7 per metro, mostly electricians and generator dealers rather than repair specialists. Moderate opening at best; storm-season demand spike is real but seasonal."),
 "land clearing": ("saturated","5-8 per metro at 5.0, developer-led with long sales cycles. Not a call-driven business."),
 "mobile mechanic": ("saturated","7 per metro, 24-hour flags everywhere, several no-website operators. Density is high enough that this is a service-quality competition, not a supply gap."),
}

NO_REVIEW_COUNTS = ("Google Maps list view does not expose review counts in this layout. "
                    "Supply strength is therefore expressed as operator count, median rating and "
                    "website presence only. Review depth requires the paid Places API.")


def parse(block):
    rows = []
    for line in block.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("__"):
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        name, phone, rating, web = (parts + ["", "", ""])[:4]
        if phone in ("-", ""):
            phone = ""
        try:
            rating_v = float(rating) if rating else None
        except ValueError:
            rating_v = None
        rows.append({"operator": name, "phone": phone,
                     "rating": rating_v,
                     "website": "yes" if web.strip() == "w" else ("no" if web.strip() == "-" else "unknown")})
    return rows


def main():
    op_rows, market_rows = [], []
    for service, metros in DATA.items():
        for metro, (region, block) in metros.items():
            rows = parse(block)
            # drop obvious cross-service contamination rows used only as context
            for r in rows:
                op_rows.append({"service": service, "metro": metro, "region": region,
                                "operator": r["operator"], "phone": r["phone"],
                                "rating": r["rating"], "website": r["website"]})
            if not rows:
                continue
            ratings = [r["rating"] for r in rows if r["rating"] is not None]
            market_rows.append({
                "service": service, "metro": metro, "region": region,
                "operators": len(rows),
                "median_rating": round(st.median(ratings), 2) if ratings else None,
                "no_website": sum(1 for r in rows if r["website"] == "no"),
                "unrated": sum(1 for r in rows if r["rating"] is None),
                "basis": "Google Maps list view",
            })

    for service, metro, region, n, med, noweb, note in AGG:
        market_rows.append({"service": service, "metro": metro, "region": region,
                            "operators": n, "median_rating": med, "no_website": noweb,
                            "unrated": None, "basis": "Google Maps list view",
                            "note": note})

    with open(os.path.join(HERE, "nefl-supply-scan.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["service", "metro", "region", "operator", "phone", "rating", "website"])
        w.writeheader()
        w.writerows(op_rows)

    with open(os.path.join(HERE, "nefl-supply-markets.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["service", "metro", "region", "operators", "median_rating",
                                          "no_website", "unrated", "basis", "note"])
        w.writeheader()
        w.writerows(market_rows)

    summary = {}
    for m in market_rows:
        s = summary.setdefault(m["service"], {"cells": 0, "operators": 0, "core": [], "fringe": [], "out": []})
        s["cells"] += 1
        s["operators"] += m["operators"]
        s[m["region"]].append(m)

    out = {
        "captured": "2026-10-22 / 2026-10-23",
        "source": "Google Maps local list view (free browser extraction, no paid API)",
        "cost_usd": 0.0,
        "limitation": NO_REVIEW_COUNTS,
        "region_legend": {
            "core": "Evan's backyard - Duval, Jacksonville Beach, St Johns, Clay, Nassau",
            "fringe": "NE Florida outer ring, still drivable",
            "out": "out-of-area comparison metros (GA/FL interior/NC/SC) - not prospects",
        },
        "assessment": {k: {"verdict": v[0], "why": v[1]} for k, v in ASSESS.items()},
        "services": {k: {"cells": v["cells"], "operator_rows": v["operators"],
                         "core_metros": len(v["core"]), "fringe_metros": len(v["fringe"]),
                         "out_metros": len(v["out"])} for k, v in summary.items()},
        "markets": market_rows,
    }
    with open(os.path.join(HERE, "nefl-supply-scan.json"), "w") as f:
        json.dump(out, f, indent=1)

    print(f"operator rows: {len(op_rows)}")
    print(f"market cells : {len(market_rows)}")
    print(f"services     : {len(summary)}")
    for k, v in sorted(summary.items(), key=lambda x: -x[1]["operators"]):
        print(f"  {k:34s} cells={v['cells']:2d} rows={v['operators']:3d} "
              f"core={len(v['core']):2d} fringe={len(v['fringe']):2d} out={len(v['out']):2d}")


if __name__ == "__main__":
    main()
