# beovox-poe

The beovox-poe project is an 80W PoE-PD PCB and panel mount for powering a [HiFiBerry Beocreate 4 channel amplifier](https://www.hifiberry.com/shop/boards/beocreate-4-channel-amplifier/) for upcycling [B&O BeoVox CX50 and CX100 speakers](https://beoworld.org/prod_details.asp?pid=482).

## The end result
- Awesome looking speakers
- AirPlay and other streaming services
- PoE-powered
![cx100-front](https://github.com/hornej/beovox-poe/blob/main/images/front.jpeg?raw=true)
![cx100-back](https://github.com/hornej/beovox-poe/blob/main/images/back.jpeg?raw=true)

# How to build it
![pcb](https://github.com/hornej/beovox-poe/blob/main/images/pcb.jpeg?raw=true)
## PCB
I designed the PCB to be ordered from [JLCPCB](https://jlcpcb.com/). You should be able to get 2-5 boards fabricated and assembled for about $100 (not including parts you will need to hand assmeble, see below). 
1. Upload the zipped Gerber file "beovox-poe-mfg-rev2.zip" to JLCPCB
2. Select the silkscreen color you want. Green is usually the cheapest and fastest.
3. Select PCB Assembly and "Assemble top side". You can do both sides if you want them to solder on the threaded standoffs (MP1, MP2, MP3, MP4) but it will cost more. 
4. Click NEXT
5. Upload BOM. *pcb-files/Project Outputs for beovox-poe/BOM/Bill of Materials-beovox-poe(assembly).csv*
6. Upload Pick and Place file. *pcb-files/Project Outputs for beovox-poe/Pick Place/Pick Place for beovox-poe(assembly).csv*
7. JLCPCB doesn't stock the AG5800 PD Module and the 1000 BaseT 4PPoE transformer so you will need to buy those separate from DigiKey or Mouser and hand assemble. 
### Parts you may need to hand assemble
- [Silvertel AG5800](https://www.digikey.com/en/products/detail/silvertel/AG5800/21187212)
- [Wurth Elektronic 7490220122](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/7490220122/6236330?s=N4IgTCBcDaIOwBYCcAGMYUEZ0gLoF8g)
- [YIYUAN SMTSOM380BTR](https://www.lcsc.com/product-detail/SMD-round-nut_YIYUAN-SMTSOM380BTR_C5301772.html). You can also get these ones ([Keystone 24885](https://www.digikey.com/en/products/detail/keystone-electronics/24885/9921825)) from DigiKey 
## Other Parts
- CX50 or CX100 speakers
- [Hifiberry 4 channel beocreate amplifier](https://www.hifiberry.com/shop/bundles/beocreate-bundle/)
    - In the bundle you will want the 3D printed mount, Mini-XLR jack 4 pin x2, Mini-XLR cable 4 pin
- M3 x 4mm threaded inserts, 4pcs. I used this assorted pack from [Amazon](https://a.co/d/7iqzvGJ)
- M3 x 10mm flat head screws, 6pcs. I used this assorted pack from [Amazon](https://a.co/d/8P6GyeA)
- CAT6 cable
- Ethernet switch with at least PoE+. You could also use a [PoE injector](https://www.lcsc.com/product-detail/Ethernet-Modules_span-style-background-color-ff0-Winchen-span-WC-PSE90B01_C2848011.html) if your switch doesn't have PoE. 
- 3D printer filament. I used this [matte white PLA](https://a.co/d/eN3NyxM)

## HiFiBerry Beocreate Amp installation
See the appropriate guide for your speakers on [GitHub](https://github.com/bang-olufsen/create/tree/master/Guides)

![pcb](https://github.com/hornej/beovox-poe/blob/main/images/internals.jpeg?raw=true)

# Repairing your speakers
Vintage speakers may need some TLC including refoaming the speakers, fixing the frames, and/or reclothing the frames. 
## Frames
You can 3D print frames for CX50/CX100 from [Thingiverse](https://www.thingiverse.com/thing:365459). 
If you are in the US, I recommend this [black speaker cloth](https://www.joann.com/utility-fabric-black-speaker-cloth/3514023.html) from Joann. It is stretchy and thin which makes it easy to work with. I used this [grey speaker cloth](https://www.parts-express.com/Speaker-Grill-Cloth-Gray-Yard-70-Wide-260-337?quantity=1&custcol1=Speaker%20Grill%20Cloth%20Gray%20Yard%2070%22%20Wide&custcol_ava_item=260-337&custcol_ava_incomeaccount=General&custcol_ava_upccode=844632040153&custcol_ava_pickup=F&custcol_disableshopping=F&undefined=16.99) for the CX100 speakers. It is a little sturdier which I also like.  
## Speaker foams
I tested out some different speaker surrounds from Amazon and eBay and they didn't fit quite right for the CX50/CX100. I highly recommend [these](https://www.repairyourspeakers.com/en/surrounds-by-size/2-4-inch/4-af-86b-rubber-surround-for-repair-speaker/a-2640-10000068) from Audiofriends. They also have this [video](https://youtu.be/A_NZoNgs02c?si=07Pem7QP0-d5mRjE) on how to replace them. 

# Future iterations / improvements
- I don't see a huge need to have the diode ORing circuit and it also adds a bit of cost relative to the rest of the SMD components. It could just use a slide switch or something to switch between POE power and Barrel jack power. 
- It would be fun to try out a USB-C PD version. 