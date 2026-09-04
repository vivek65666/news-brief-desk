from datetime import datetime, timedelta, timezone


def relative_timestamp(days_back: int = 0, hour: int = 8, minute: int = 0) -> str:
    now = datetime.now(timezone.utc)
    base = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if days_back:
        base = base - timedelta(days=days_back)
    return base.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_sample_raw_items():
    return [
        {
            "source_name": "Reuters",
            "source_type": "wire copy",
            "headline": "Bengaluru Metro says signalling fault has disrupted services on Purple Line",
            "content": "Bengaluru Metro officials said a signalling issue near the Majestic interchange caused a temporary suspension of services on the Purple Line during the morning rush. Commuters were advised to expect delays and crowding at stations as technicians worked to restore normal operations.",
            "received_at": relative_timestamp(days_back=1, hour=7, minute=42),
            "status": "INCOMING",
        },
        {
            "source_name": "The Hindu",
            "source_type": "news desk",
            "headline": "Metro commuters face delays as Bengaluru transport authority reports signal problem",
            "content": "Commuters on the Purple Line in Bengaluru faced long waits after the city transport authority reported a signalling problem near a key interchange. Officials said trains were running at reduced headways while engineers inspected the control system.",
            "received_at": relative_timestamp(days_back=1, hour=8, minute=5),
            "status": "INCOMING",
        },
        {
            "source_name": "City Desk",
            "source_type": "social post",
            "headline": "Commuters stuck as Bengaluru Metro service slows after signal fault",
            "content": "People travelling on Bengaluru Metro were stuck in packed stations this morning after a signal issue disrupted service on the Purple Line. Several commuters said trains were moving slowly while staff directed passengers away from crowded platforms.",
            "received_at": relative_timestamp(days_back=1, hour=8, minute=41),
            "status": "INCOMING",
        },
        {
            "source_name": "Associated Press",
            "source_type": "wire copy",
            "headline": "City airport authority cancels flights after overnight storm brings heavy rain",
            "content": "The city airport authority said operations were temporarily disrupted after an overnight storm brought heavy rain and strong crosswinds to the region. Several flights were delayed, and ground crews were working to clear standing water on taxiways.",
            "received_at": relative_timestamp(days_back=2, hour=6, minute=10),
            "status": "INCOMING",
        },
        {
            "source_name": "Metro News",
            "source_type": "press release",
            "headline": "Water board extends emergency pumping plan after flooding in low-lying neighborhoods",
            "content": "The city water utility said it had extended emergency pumping operations in low-lying neighborhoods after heavy rain caused surface flooding. Residents were asked to avoid certain roads and waterlogged underpasses while crews worked to clear drains.",
            "received_at": relative_timestamp(days_back=1, hour=9, minute=2),
            "status": "INCOMING",
        },
        {
            "source_name": "Government Press Office",
            "source_type": "press release",
            "headline": "State health department launches mosquito-control drive in urban wards",
            "content": "Officials said public health teams had started a mosquito-control drive in urban wards after a rise in complaints about stagnant water. The department said fogging and source reduction work would continue over the next three days.",
            "received_at": relative_timestamp(days_back=0, hour=10, minute=18),
            "status": "INCOMING",
        },
        {
            "source_name": "TechWire",
            "source_type": "blog",
            "headline": "Startup founders urge faster approvals for EV charging hubs in the city",
            "content": "Industry executives said city agencies should speed up approvals for private electric-vehicle charging hubs as commercial demand grows. They argued that costly delays in permitting were slowing deployment in dense residential clusters.",
            "received_at": relative_timestamp(days_back=0, hour=11, minute=10),
            "status": "INCOMING",
        },
        {
            "source_name": "Reuters",
            "source_type": "wire copy",
            "headline": "Chennai Metro service disrupted after signalling fault near central station",
            "content": "Metro officials in Chennai said a signalling fault near the central station disrupted train movement on the Blue Line on Tuesday morning. Trains were being operated with manual controls and passengers were asked to expect delays on the route.",
            "received_at": relative_timestamp(days_back=1, hour=7, minute=52),
            "status": "INCOMING",
        },
        {
            "source_name": "BBC News",
            "source_type": "news desk",
            "headline": "Chennai commuters delayed as metro trains run slowly after signal warning",
            "content": "A signal warning near central Chennai slowed services on the Blue Line, causing delays for commuters heading to work. Officials said the issue was being investigated and that the rail operator had reduced speeds between two stations.",
            "received_at": relative_timestamp(days_back=1, hour=8, minute=14),
            "status": "INCOMING",
        },
        {
            "source_name": "Business Daily",
            "source_type": "news desk",
            "headline": "Regional logistics startup secures funding for cold-chain network expansion",
            "content": "A regional cold-chain startup announced a new funding round to expand refrigerated logistics across the state. The company said the investment would support warehouse upgrades, longer-haul delivery routes and a wider network of refrigerated distribution centres.",
            "received_at": relative_timestamp(days_back=0, hour=12, minute=4),
            "status": "INCOMING",
        },
        {
            "source_name": "Indian Express",
            "source_type": "news desk",
            "headline": "City schools postpone sports day after heat advisory remains in effect",
            "content": "Several city schools postponed sports events planned for Wednesday after the weather office extended a heat advisory through the afternoon. Administrators said students would take part in indoor activities instead while conditions remained severe.",
            "received_at": relative_timestamp(days_back=0, hour=9, minute=46),
            "status": "INCOMING",
        },
        {
            "source_name": "Metro News",
            "source_type": "social post",
            "headline": "School sports day moved indoors as heat advisory continues across the city",
            "content": "Parents in the city said several schools shifted sporty events indoors after authorities warned of high afternoon temperatures. School officials said the change was made to protect students during the ongoing heat advisory.",
            "received_at": relative_timestamp(days_back=0, hour=10, minute=5),
            "status": "INCOMING",
        },
        {
            "source_name": "The Hindu",
            "source_type": "news desk",
            "headline": "Coastal district chief minister visits flood-hit villages after monsoon rains",
            "content": "The chief minister toured flood-hit villages in a coastal district on Monday to assess damage after heavy monsoon rainfall. Officials said emergency teams were distributing relief materials and restoring access roads in the hardest-hit areas.",
            "received_at": relative_timestamp(days_back=2, hour=13, minute=9),
            "status": "INCOMING",
        },
        {
            "source_name": "Associated Press",
            "source_type": "wire copy",
            "headline": "Chief minister inspects flood relief operations in coastal district after heavy rainfall",
            "content": "The chief minister inspected relief efforts in a coastal district after several villages were hit by monsoon rainfall and local flooding. Officials said power restoration, food distribution and road clearance operations remained underway.",
            "received_at": relative_timestamp(days_back=2, hour=13, minute=33),
            "status": "INCOMING",
        },
        {
            "source_name": "City Desk",
            "source_type": "social post",
            "headline": "Villagers in coastal belt report road damage as rain continues",
            "content": "Residents in the coastal belt said roads were still cut off after persistent rainfall and flooding. Volunteers and municipal workers were clearing mud from damaged stretches while families waited for relief supplies.",
            "received_at": relative_timestamp(days_back=2, hour=14, minute=2),
            "status": "INCOMING",
        },
        {
            "source_name": "Government Press Office",
            "source_type": "press release",
            "headline": "State transport department opens emergency bus links for flood-hit residents",
            "content": "The state transport department said it had opened emergency bus services to connect villages cut off by flooding with district relief centres. Officials said the service would remain in place while roads were being repaired.",
            "received_at": relative_timestamp(days_back=1, hour=14, minute=28),
            "status": "INCOMING",
        },
        {
            "source_name": "Reuters",
            "source_type": "wire copy",
            "headline": "Hospital chain expands emergency care unit after rising patient demand",
            "content": "A hospital chain said it had opened additional emergency beds and expanded triage capacity after a surge in patient demand during the monsoon season. The company said the move was aimed at reducing waiting times in crowded facilities.",
            "received_at": relative_timestamp(days_back=0, hour=15, minute=10),
            "status": "INCOMING",
        },
        {
            "source_name": "BBC News",
            "source_type": "news desk",
            "headline": "Hospital network adds beds as seasonal illness cases rise in the city",
            "content": "City hospitals reported a rise in seasonal respiratory and fever cases, prompting one network to add emergency beds and expand observation units. Staff said patient flow remained heavy and the extra capacity would help ease congestion.",
            "received_at": relative_timestamp(days_back=0, hour=15, minute=35),
            "status": "INCOMING",
        },
        {
            "source_name": "Indian Express",
            "source_type": "news desk",
            "headline": "Public transport strike enters second day as workers demand revised pay scale",
            "content": "Transport workers entered a second day of action on Thursday, demanding a revised pay scale and better working conditions. Commuters reported crowded buses and delays as city agencies tried to manage the disruption without full service levels.",
            "received_at": relative_timestamp(days_back=1, hour=16, minute=1),
            "status": "INCOMING",
        },
        {
            "source_name": "Business Daily",
            "source_type": "blog",
            "headline": "Commuters face long delays as public bus strike continues across the city",
            "content": "City commuters faced long waits and crowded roads as a bus strike continued into its second day. Officials said transit operators were redeploying limited services, but many routes remained severely affected.",
            "received_at": relative_timestamp(days_back=1, hour=16, minute=20),
            "status": "INCOMING",
        },
        {
            "source_name": "City Desk",
            "source_type": "social post",
            "headline": "Traffic gridlock spreads as bus strike disrupts morning commute",
            "content": "Residents reported severe congestion on major roads after a bus strike disrupted the morning commute. Riders said they were leaving home earlier and using ride-sharing services to reach work as transport remained uneven.",
            "received_at": relative_timestamp(days_back=1, hour=16, minute=45),
            "status": "INCOMING",
        },
        {
            "source_name": "The Hindu",
            "source_type": "news desk",
            "headline": "Government approves new coastal protection plan after storm damage",
            "content": "The government approved a coastal protection plan aimed at reducing storm damage in vulnerable communities after recent high-wind conditions. Officials said the proposal focused on strengthening embankments, drainage and disaster response planning.",
            "received_at": relative_timestamp(days_back=0, hour=17, minute=15),
            "status": "INCOMING",
        },
        {
            "source_name": "Press Watch",
            "source_type": "press release",
            "headline": "State approves coastal protection works after storm-hit villages seek repairs",
            "content": "Officials said the state had approved a coastal protection programme after storm-hit villages warned of worsening erosion and drainage failures. Engineers said the scheme would fund flood barriers, drainage repairs and embankment strengthening over the next year.",
            "received_at": relative_timestamp(days_back=0, hour=17, minute=42),
            "status": "INCOMING",
        },
    ]


SAMPLE_RAW_ITEMS = build_sample_raw_items()
