import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from rag.schemas import FAQItem

DEFAULT_CHUNKS: list[dict[str, Any]] = [
    {
        "section_id": "1.1",
        "title": "Section 1.1: Event Snapshot & Overview",
        "category": "Event Overview",
        "keywords": ["format", "duration", "hours", "theme", "venue", "location", "dates", "timing", "when", "where", "in-person", "schedule", "36 hours"],
        "content": (
            "**Innovate AI Hackathon 2026 Snapshot:**\n"
            "- **Format:** In-person, 36 hours (Day 1, 9:00 AM – Day 2, 9:00 PM).\n"
            "- **Theme:** *Applied Artificial Intelligence for Real-World Impact*.\n"
            "- **Eligibility:** Currently enrolled undergraduate and postgraduate students.\n"
            "- **Team Size:** 2 to 4 members per team (solo participation is not permitted).\n"
            "- **Venue:** Main Campus Auditorium & Innovation Labs (Blocks A–C).\n"
            "- **Registration:** Online via the official portal with team and member verification."
        ),
        "suggested_questions": [
            "What is the allowed team size?",
            "What is the venue and schedule?",
            "Can I participate as a solo developer?"
        ]
    },
    {
        "section_id": "1.2",
        "title": "Section 1.2: Guiding Principles",
        "category": "Event Overview",
        "keywords": ["principles", "fairness", "safety", "transparency", "inclusivity", "responsible ai", "ethics", "bias"],
        "content": (
            "**Core Guiding Principles:**\n"
            "- **Fairness:** Every team competes under identical rules, resources, and time limits.\n"
            "- **Safety:** Physical and emotional safety of every participant takes priority over the event schedule.\n"
            "- **Transparency:** Judging criteria, prize structure, and policies are published in advance and not changed mid-event.\n"
            "- **Inclusivity:** The event welcomes participants regardless of background, identity, or experience level.\n"
            "- **Responsible AI:** Participants are encouraged to consider ethics, bias, and safety in what they build."
        ),
        "suggested_questions": [
            "What are the judging criteria?",
            "What is the code of conduct?"
        ]
    },
    {
        "section_id": "2.1",
        "title": "Section 2.1: Who Can Participate & Eligibility",
        "category": "Eligibility & Registration",
        "keywords": ["eligibility", "student", "college", "university", "age", "minor", "under 18", "working professional", "open track", "id card", "who can participate", "requirements"],
        "content": (
            "**Participant Eligibility Rules:**\n"
            "- **Student Status:** Must be currently enrolled students (undergraduate, postgraduate, or diploma) at a recognized institution at the time of the event.\n"
            "- **Verification:** A valid college/university ID card must be presented at on-site check-in.\n"
            "- **Age Limit:** Minimum age of 17 applies (no upper age limit). Participants under 18 must submit a signed parental/guardian consent form before check-in.\n"
            "- **Working Professionals:** May participate only in designated 'Open Track' if announced separately; Student Track is strictly for enrolled students."
        ),
        "suggested_questions": [
            "Can working professionals participate?",
            "What documents are required at check-in?",
            "What is the minimum age to participate?"
        ]
    },
    {
        "section_id": "2.2",
        "title": "Section 2.2: Team Formation & Size Limits",
        "category": "Eligibility & Registration",
        "keywords": ["team", "team size", "solo", "alone", "individual", "members", "teammates", "cross college", "cross city", "team lock", "change team", "team finder"],
        "content": (
            "**Team Formation & Guidelines:**\n"
            "- **Team Size:** Minimum 2 and maximum 4 members. Solo participation is **NOT** permitted under any circumstances.\n"
            "- **Cross-College Teams:** Cross-college and cross-city teams are fully permitted.\n"
            "- **One Team Rule:** Each participant may register with only one team. Registering with multiple teams results in removal from all teams.\n"
            "- **Finding Teammates:** Use the 'Team Finder' channel on the event Discord/WhatsApp community prior to the event.\n"
            "- **Team Lock:** Team composition is locked **24 hours before the event start**. No swaps or additions are permitted after this point (except in case of withdrawal reported to the organizing desk)."
        ),
        "suggested_questions": [
            "Can I participate alone?",
            "Can my team have members from different colleges?",
            "Can I change my team after registering?"
        ]
    },
    {
        "section_id": "2.3",
        "title": "Section 2.3: Registration Process & Team ID",
        "category": "Eligibility & Registration",
        "keywords": ["registration process", "how to register", "team id", "account", "abstract", "confirmation email", "details required"],
        "content": (
            "**Registration Steps:**\n"
            "1. Create an account on the official registration website.\n"
            "2. Fill in individual details for all team members (name, institution, year, email, phone, dietary preference, T-shirt size).\n"
            "3. Submit a one-line idea abstract (optional at registration; mandatory before the event for track allocation).\n"
            "4. Pay registration fee (if applicable) via the payment gateway.\n"
            "5. Receive confirmation email with a unique **Team ID** (required for check-in, communication, and support tickets)."
        ),
        "suggested_questions": [
            "What is the Team ID used for?",
            "What information is needed during registration?"
        ]
    },
    {
        "section_id": "2.4",
        "title": "Section 2.4: Registration Deadlines & Schedule",
        "category": "Eligibility & Registration",
        "keywords": ["deadlines", "early bird", "closing date", "schedule", "check-in window", "timeline", "dates"],
        "content": (
            "**Important Registration Deadlines:**\n"
            "- **Early-bird Registration Closes:** 2 weeks before event.\n"
            "- **Final Registration Closes:** 3 days before event.\n"
            "- **Team Lock & Idea Abstract Due:** 24 hours before event.\n"
            "- **On-site Check-in Window:** Day 1, 7:00 AM – 8:45 AM."
        ),
        "suggested_questions": [
            "When does registration close?",
            "What time is on-site check-in on Day 1?"
        ]
    },
    {
        "section_id": "2.5",
        "title": "Section 2.5: Fees, Cancellations & Refunds",
        "category": "Eligibility & Registration",
        "keywords": ["fee", "cancellation", "refund", "money back", "transfer ticket", "no show", "policy"],
        "content": (
            "**Fee, Cancellation & Refund Policy:**\n"
            "- **Fee Coverage:** Covers participation, all meals/refreshments, and event kit for the full 36 hours.\n"
            "- **Cancellations 7+ Days Before:** Eligible for full refund minus payment gateway charges.\n"
            "- **Cancellations within 7 Days:** Non-refundable, but may be transferred once to another eligible student by notifying organizers.\n"
            "- **No-Shows:** Not eligible for any refund."
        ),
        "suggested_questions": [
            "Can I get a refund if I cancel?",
            "Can I transfer my registration to another student?"
        ]
    },
    {
        "section_id": "3.1",
        "title": "Section 3.1: Problem Statements & Tracks",
        "category": "Rules & Regulations",
        "keywords": ["tracks", "problem statements", "themes", "healthcare", "fintech", "climate", "agentic tools", "accessibility", "open innovation", "original problem"],
        "content": (
            "**Tracks & Problem Statements:**\n"
            "Teams may choose from officially published tracks or propose an original problem statement (subject to organizer approval before hacking starts):\n"
            "- 🏥 **Healthcare AI:** Diagnostics, patient care, mental health, bio-assistants.\n"
            "- 💳 **FinTech AI:** Fraud detection, financial literacy, automated budgeting, smart underwriting.\n"
            "- 🌍 **Climate & Sustainability:** Carbon tracking, energy optimization, waste management.\n"
            "- 🤖 **Agentic Tools & Automation:** Multi-agent workflows, developer productivity, autonomous assistants.\n"
            "- ♿ **Accessibility:** Assistive tech, voice/vision inclusivity, sign-language solutions.\n"
            "- 💡 **Open Innovation:** Novel AI applications solving meaningful real-world challenges.\n\n"
            "*Note: Track selection is locked once hacking begins and cannot be changed.*"
        ),
        "suggested_questions": [
            "What are the hackathon tracks?",
            "Can we propose our own problem statement?",
            "Can we switch tracks after hacking starts?"
        ]
    },
    {
        "section_id": "3.2",
        "title": "Section 3.2: Permitted Tools, Hardware & APIs",
        "category": "Rules & Regulations",
        "keywords": ["what can i bring", "allowed tools", "hardware", "laptops", "cloud apis", "pre-trained models", "open source", "openai", "anthropic", "google", "aws", "azure", "libraries"],
        "content": (
            "**What You May Bring and Use:**\n"
            "- **Hardware:** Personal laptops, chargers, mice, headphones, and personal peripherals.\n"
            "- **Open-Source:** Libraries, frameworks, and public datasets (with proper licensing and attribution).\n"
            "- **Pre-Trained AI Models:** Open-weight LLMs, computer vision models, embeddings as foundations, provided the team's application logic, fine-tuning, prompt engineering, or integration is original and built during the event.\n"
            "- **Cloud AI APIs:** OpenAI, Anthropic, Google, AWS, Azure within free-tier or provided sponsor credits."
        ),
        "suggested_questions": [
            "Can I use pre-trained AI models?",
            "Are cloud AI APIs allowed?",
            "What hardware should I bring?"
        ]
    },
    {
        "section_id": "3.3",
        "title": "Section 3.3: Prohibited Actions & What is Not Allowed",
        "category": "Rules & Regulations",
        "keywords": ["not allowed", "prohibited", "banned", "pre-built code", "plagiarism", "fake demo", "pre-recorded", "cheating", "impersonation", "hacking infrastructure"],
        "content": (
            "**What Is NOT Allowed (Strict Violations):**\n"
            "1. **Pre-built Projects:** Submitting code, models, or product features built prior to the hackathon start. (Fresh framework boilerplate scaffolding is allowed).\n"
            "2. **Plagiarism:** Copying another team's idea, code, or design without attribution.\n"
            "3. **Fake Demos:** Pre-recording responses and pretending they are live model outputs.\n"
            "4. **Security Attacks:** Disrupting or probing event infrastructure, sponsor servers, or other teams' devices without written authorization.\n"
            "5. **Impersonation:** Using another person's credentials or having outside individuals code on your behalf."
        ),
        "suggested_questions": [
            "Can I use code written before the hackathon?",
            "What happens if a team plagiarizes?"
        ]
    },
    {
        "section_id": "3.4",
        "title": "Section 3.4: Responsible & Permitted Use of AI Tools",
        "category": "Rules & Regulations",
        "keywords": ["chatgpt", "claude", "copilot", "ai assistants", "generative ai", "ai coding", "ai tools", "allowed ai", "code generation", "llm tools", "can i use chatgpt"],
        "content": (
            "**Use of AI Coding Assistants (ChatGPT, Claude, GitHub Copilot):**\n"
            "- **Explicitly Permitted & Encouraged:** As this is an AI hackathon, the use of AI assistants and generative coding tools is **100% allowed**.\n"
            "- **Defensibility Requirement:** Teams must understand and be able to defend/explain every component of their submitted code and architecture during judging.\n"
            "- **Unexplained Code Penalty:** AI-generated code that a team cannot explain will be scored as unoriginal work.\n"
            "- **Disclosure:** All 3rd-party models, datasets, and APIs used must be disclosed in the final submission form."
        ),
        "suggested_questions": [
            "Am I allowed to use ChatGPT or Claude to help me code?",
            "Do I have to disclose AI tools used in my project?",
            "Will judges ask questions about AI-generated code?"
        ]
    },
    {
        "section_id": "3.5",
        "title": "Section 3.5: Code of Conduct & Anti-Harassment Policy",
        "category": "Rules & Regulations",
        "keywords": ["code of conduct", "harassment", "zero tolerance", "safety", "discrimination", "inappropriate", "reporting harassment", "conduct policy"],
        "content": (
            "**Code of Conduct & Anti-Harassment Policy:**\n"
            "- **Zero-Tolerance:** Zero tolerance for harassment, intimidation, offensive comments, stalking, or inappropriate behavior in all physical and digital event spaces.\n"
            "- **Enforcement:** Organizers may issue warnings, expel offenders without refund, and escalate to campus security or law enforcement.\n"
            "- **Reporting:** Approach any staff member wearing an organizer lanyard, visit the 24/7 Help Desk, or use the confidential online reporting channel."
        ),
        "suggested_questions": [
            "How do I report harassment or safety concerns?",
            "What is the event code of conduct?"
        ]
    },
    {
        "section_id": "3.6",
        "title": "Section 3.6: Project Submission Rules & Requirements",
        "category": "Rules & Regulations",
        "keywords": ["submission", "how to submit", "github", "demo video", "slides", "deck", "deadline", "late submission", "readme", "submission package"],
        "content": (
            "**Submission Rules & Required Package:**\n"
            "- **Platform:** Must be pushed to a public or organizer-accessible GitHub repository.\n"
            "- **Package Requirements:**\n"
            "  1. Clean source code.\n"
            "  2. `README.md` with setup and execution instructions.\n"
            "  3. 2–3 minute video demo demonstrating live functionality.\n"
            "  4. Slide deck (maximum 10 slides).\n"
            "- **Strict Deadline:** Late submissions are **NOT accepted under any circumstance**. Teams should submit at least 30 minutes prior to deadline.\n"
            "- **One Submission:** Only one final submission per team is scored."
        ),
        "suggested_questions": [
            "What must be included in the submission package?",
            "What happens if we submit 1 minute late?",
            "How long should the demo video be?"
        ]
    },
    {
        "section_id": "3.8",
        "title": "Section 3.8: Disqualification Matrix",
        "category": "Rules & Regulations",
        "keywords": ["disqualification", "violations", "penalties", "punishment", "banned", "expulsion"],
        "content": (
            "**Disqualification Criteria:**\n"
            "| Violation | Consequence |\n"
            "|---|---|\n"
            "| Plagiarism or pre-built project | Immediate disqualification |\n"
            "| Harassment or Code of Conduct breach | Warning, expulsion, or security escalation |\n"
            "| Sabotage of another team/infra | Immediate disqualification & possible future ban |\n"
            "| Late submission | Submission will not be scored |\n"
            "| Undisclosed banned tools/datasets | Score penalty or disqualification |"
        ),
        "suggested_questions": [
            "What leads to immediate disqualification?",
            "Can late submissions be scored?"
        ]
    },
    {
        "section_id": "4.1",
        "title": "Section 4.1 & 4.2: Judging Rounds & Scoring Rubric",
        "category": "Judging & Scoring",
        "keywords": ["judging", "scoring", "rubric", "criteria", "weights", "rounds", "finals", "demo", "presentation", "how are we evaluated", "evaluation"],
        "content": (
            "**Judging Process & Official 100% Scoring Rubric:**\n"
            "- **Round 1 (Mentor Screening):** Completeness check & track fit (feedback provided; no elimination).\n"
            "- **Round 2 (Preliminary Scoring):** Panel scores all submissions against rubric; top teams advance.\n"
            "- **Round 3 (Finals):** Shortlisted teams present a live 5-minute demo + 3-minute Q&A to the grand jury.\n\n"
            "**Scoring Weights:**\n"
            "- 🌟 **Innovation & Originality (25%):** Novelty and uniqueness compared to existing solutions.\n"
            "- ⚙️ **Technical Implementation (25%):** Working prototype, clean architecture, sound use of AI/ML.\n"
            "- 🎯 **Real-World Impact & Feasibility (20%):** Practical utility, market viability, scalability.\n"
            "- 🎨 **User Experience & Design (15%):** Intuitive UI, usability, interaction polish.\n"
            "- 🎤 **Presentation & Demo (15%):** Pitch clarity, live demo quality, response to judge questions."
        ),
        "suggested_questions": [
            "What is the judging criteria and scoring breakdown?",
            "How long is the final presentation demo?",
            "Can I appeal my score if there is a mistake?"
        ]
    },
    {
        "section_id": "4.4",
        "title": "Section 4.4: Scoring Disputes & Appeals",
        "category": "Judging & Scoring",
        "keywords": ["dispute", "appeal", "scoring error", "complaint", "re-evaluation", "chief judge"],
        "content": (
            "**Scoring Disputes & Appeal Process:**\n"
            "- Judging decisions are final, but teams who suspect an objective scoring error may file a written appeal at the Help Desk within **1 hour** of results announcement.\n"
            "- The Chief Judge and Event Director will review and issue a formal response within 24 hours."
        ),
        "suggested_questions": [
            "How do I appeal a judging score?",
            "What is the deadline to file a scoring appeal?"
        ]
    },
    {
        "section_id": "5.1",
        "title": "Section 5.1 & 5.2: Venue Facilities, Wi-Fi & Compute Resources",
        "category": "Logistics & Facilities",
        "keywords": ["venue", "wifi", "internet", "power", "charging", "nap area", "sleep", "quiet zone", "gpu", "cloud credits", "compute", "aws", "gcp", "azure"],
        "content": (
            "**Venue, Facilities & Compute Logistics:**\n"
            "- **Hacking Area:** Innovation Labs, Blocks A–C with dedicated team tables, power strips, and high-speed Wi-Fi.\n"
            "- **Backup Connectivity:** Wired Ethernet backup stations available at Help Desk.\n"
            "- **Rest Zones:** Dedicated quiet zones and nap areas equipped for overnight rests.\n"
            "- **Cloud Credits:** Sponsor cloud credits (AWS, GCP, Azure, or OpenAI/Anthropic API credits) distributed at check-in.\n"
            "- **GPU Stations:** Limited GPU machines available on first-come, first-served booking at the Help Desk."
        ),
        "suggested_questions": [
            "Is there a place to sleep or nap during the hackathon?",
            "Are GPU machines and cloud credits provided?",
            "What is the Wi-Fi setup at the venue?"
        ]
    },
    {
        "section_id": "5.3",
        "title": "Section 5.3: Food, Catering & Refreshments",
        "category": "Logistics & Facilities",
        "keywords": ["food", "meals", "dinner", "breakfast", "lunch", "snacks", "tea", "coffee", "drinks", "vegan", "vegetarian", "jain", "diet", "dietary", "midnight snack", "unlimited coffee"],
        "content": (
            "**Food & Catering Details:**\n"
            "- **Included Meals:** Full catering is provided for the entire 36 hours at no extra cost:\n"
            "  - Day 1: Dinner & Midnight snacks.\n"
            "  - Day 2: Breakfast, Lunch, and Dinner.\n"
            "  - Continuous 24/7: Tea, coffee, and water stations throughout the venue.\n"
            "- **Dietary Preferences:** Vegetarian, Vegan, Jain, Gluten-free, and allergy accommodations are prepared according to registration records.\n"
            "- **Dining Areas:** Food must be consumed in designated dining zones to protect laptops and lab equipment."
        ),
        "suggested_questions": [
            "Is food provided during the event?",
            "Are tea and coffee available 24/7?",
            "Can I get vegan or Jain food?"
        ]
    },
    {
        "section_id": "5.4",
        "title": "Section 5.4 & 5.5: Accommodation & Travel",
        "category": "Logistics & Facilities",
        "keywords": ["accommodation", "stay", "dorm", "hotel", "rooms", "outstation", "travel", "shuttle", "bus", "train", "reimbursement"],
        "content": (
            "**Accommodation & Travel Info:**\n"
            "- **Dormitory Accommodation:** Available for outstation participants who requested it during registration (gender-segregated with dedicated floor wardens).\n"
            "- **Check-in for Stay:** Opens the evening prior to Day 1 with college ID.\n"
            "- **Bedding:** Basic bedding provided; bring toiletries and change of clothes.\n"
            "- **Travel & Shuttles:** Participants arrange their own travel. Station shuttles between the local railway/bus terminals and the venue run on scheduled timings published on the site."
        ),
        "suggested_questions": [
            "Is accommodation available for outstation students?",
            "Is travel reimbursed?",
            "Is there a shuttle from the railway station?"
        ]
    },
    {
        "section_id": "5.6",
        "title": "Section 5.6 & 5.7: Mentorship, Health & First Aid",
        "category": "Logistics & Facilities",
        "keywords": ["mentors", "mentor support", "medical", "first aid", "doctor", "health", "safety", "emergency", "fire exit"],
        "content": (
            "**Mentorship & Health Support:**\n"
            "- **Mentors:** Industry experts and professors are available 24/7 at the Mentor Desk and bookable in 15-minute 1-on-1 sprint slots via the app.\n"
            "- **First Aid Station:** Staffed around the clock by certified medical personnel.\n"
            "- **Emergency Helpline:** Printed on participant badge and posted at all lab entrances."
        ),
        "suggested_questions": [
            "How can we get help from mentors?",
            "Is there a medical team on-site?"
        ]
    },
    {
        "section_id": "6.1",
        "title": "Section 6: Complaints, Grievance Redressal & Escalation",
        "category": "Support & Redressal",
        "keywords": ["complaints", "help desk", "support", "ticket", "grievance", "escalation", "emergency contact", "harassment report"],
        "content": (
            "**Support Channels & Escalation Matrix:**\n"
            "- **Help Desk (24/7):** In-person support in Block A lobby for tech, facility, and general issues.\n"
            "- **Digital Tickets:** Submit via the 'Support' tab on the portal using your Team ID.\n"
            "- **Confidential Form:** Anonymous/sensitive reporting for safety or conduct concerns.\n\n"
            "**Escalation Timelines:**\n"
            "- **Level 1 (Help Desk Volunteer):** Immediate resolution.\n"
            "- **Level 2 (Track Coordinator):** Within 30 minutes.\n"
            "- **Level 3 (Organizing Committee / Director):** Within 2 hours.\n"
            "- **Level 4 (Code of Conduct / Safety):** Chief Organizer & Security immediately."
        ),
        "suggested_questions": [
            "Where is the Help Desk located?",
            "How quickly are support tickets resolved?",
            "How do I submit a confidential report?"
        ]
    },
    {
        "section_id": "7.1",
        "title": "Section 7.1 & 7.2: Prizes, Recognition & Disbursement",
        "category": "Prizes & Awards",
        "keywords": ["prizes", "prize pool", "cash prize", "winner", "runner up", "awards", "trophy", "internship", "tax", "tds", "disbursement", "when do we get money"],
        "content": (
            "**Prize Categories & Disbursement Terms:**\n"
            "- 🏆 **Grand Winner (1st Place):** Top cash prize, trophy, cloud credits, fast-tracked sponsor internship interviews.\n"
            "- 🥈 **1st Runner-Up (2nd Place):** Cash prize, trophy, cloud credits.\n"
            "- 🥉 **2nd Runner-Up (3rd Place):** Cash prize, trophy.\n"
            "- 🎯 **Track Winners:** Best solution awards across Healthcare, FinTech, Sustainability, Agentic Tools, Accessibility.\n"
            "- 🌟 **Special Awards:** Best Beginner Team, People's Choice Award.\n"
            "- **Disbursement:** Cash prizes transferred via bank transfer within **30 working days** (subject to ID/bank verification and statutory TDS tax deduction)."
        ),
        "suggested_questions": [
            "What are the prize categories?",
            "When will cash prizes be disbursed?",
            "Are internship interviews offered to winners?"
        ]
    },
    {
        "section_id": "7.3",
        "title": "Section 7.3 & 7.4: Certificates & Results",
        "category": "Prizes & Awards",
        "keywords": ["certificate", "participation certificate", "achievement", "contribution", "when are certificates sent", "results"],
        "content": (
            "**Certificates & Results Announcement:**\n"
            "- **Participation Certificate:** Awarded to all participants who check in on-site and submit a valid project.\n"
            "- **Achievement Certificate:** Awarded to all award and track winners.\n"
            "- **Delivery:** Issued digitally within 7 days post-event to registered email addresses.\n"
            "- **Results:** Announced live at closing ceremony and published on the website within 24 hours."
        ),
        "suggested_questions": [
            "Does everyone get a participation certificate?",
            "When are digital certificates emailed?"
        ]
    },
    {
        "section_id": "8.1",
        "title": "Section 8: Intellectual Property, Privacy & Data",
        "category": "Legal & IP",
        "keywords": ["ip", "intellectual property", "ownership", "who owns code", "copyright", "privacy", "data", "photo consent"],
        "content": (
            "**Intellectual Property & Legal Policies:**\n"
            "- **100% Participant IP:** Participants retain full ownership and intellectual property rights to the projects and code they create during the hackathon.\n"
            "- **Organizer License:** Organizers are granted a non-exclusive promotional license to feature, demo, and showcase projects in post-event media.\n"
            "- **Data Privacy:** Personal data is strictly used for event operations and opt-in recruiter matching only.\n"
            "- **Photo Consent:** Attendees consent to event photography. If you wish to opt out, request a 'No Photo' sticker for your badge at check-in."
        ),
        "suggested_questions": [
            "Who owns the intellectual property of our project?",
            "Can organizers or sponsors claim our code?",
            "How is participant personal data protected?"
        ]
    },
    {
        "section_id": "10-faq",
        "title": "Section 10: Frequently Asked Questions (Official KB)",
        "category": "FAQs",
        "keywords": ["faq", "frequently asked", "questions", "common questions", "sleep", "nap", "alone", "ai build itself", "coffee", "vegan"],
        "content": (
            "**Official FAQ Highlights:**\n"
            "- **Q: Can I participate alone?** A: No, teams must have 2 to 4 members.\n"
            "- **Q: Can I use ChatGPT / Claude?** A: Yes! AI coding assistants are fully permitted. You must understand and explain your code.\n"
            "- **Q: Is food & coffee provided?** A: Yes, all meals, midnight snacks, and continuous tea/coffee are provided.\n"
            "- **Q: Can my AI code everything while I sleep?** A: Nice try! You must defend and explain every architecture decision during judging.\n"
            "- **Q: Is there a quiet space to nap?** A: Yes, quiet zones and rest areas are available in the venue."
        ),
        "suggested_questions": [
            "Can I participate alone?",
            "Can I use ChatGPT or Claude?",
            "Is food and coffee provided?"
        ]
    },
    {
        "section_id": "appendix-a",
        "title": "Appendix A: Emergency & Key Contacts",
        "category": "Support & Contacts",
        "keywords": ["contacts", "emergency", "phone", "helpline", "chief organizer", "medical emergency", "police", "help desk contact"],
        "content": (
            "**Key Contacts & Emergency Numbers:**\n"
            "- **Emergency Helpline:** Printed on participant badge (Available 24/7 for medical/safety incidents).\n"
            "- **Help Desk:** In-person at Block A Auditorium Lobby (24/7 during event).\n"
            "- **Confidential Complaint Form:** Accessible via the portal navigation bar.\n"
            "- **Track Coordinators:** Listed in the event dashboard per track.\n"
            "- **Chief Organizer & Event Director:** Available via the Help Desk for Level 3 & 4 escalations."
        ),
        "suggested_questions": [
            "What is the emergency helpline number?",
            "Where is the physical help desk located?"
        ]
    }
]

FAQ_LIST: list[FAQItem] = [
    FAQItem(
        category="Eligibility",
        question="Can I participate as a solo developer?",
        answer="No, solo participation is not allowed. Teams must have between 2 and 4 members (Section 2.2).",
        section_id="2.2"
    ),
    FAQItem(
        category="Rules & AI",
        question="Am I allowed to use AI tools like ChatGPT or Claude?",
        answer="Yes! AI coding assistants are 100% permitted. You just need to be able to explain and defend your code during judging (Section 3.4).",
        section_id="3.4"
    ),
    FAQItem(
        category="Logistics",
        question="Is food and accommodation provided?",
        answer="Yes! All meals, snacks, and 24/7 tea/coffee are included. Dormitory accommodation is available for outstation students who requested it (Sections 5.3 & 5.4).",
        section_id="5.3"
    ),
    FAQItem(
        category="Judging",
        question="What is the scoring rubric breakdown?",
        answer="Innovation (25%), Technical Implementation (25%), Real-World Impact (20%), UX/Design (15%), and Presentation/Demo (15%) (Section 4.2).",
        section_id="4.2"
    ),
    FAQItem(
        category="Prizes",
        question="When is prize money disbursed and who owns the project IP?",
        answer="Winners receive cash prizes via bank transfer within 30 working days. Participants retain 100% ownership and IP of their code (Sections 7.2 & 8.1).",
        section_id="7.1"
    ),
    FAQItem(
        category="Fun",
        question="Can my AI build itself while I sleep?",
        answer="Nice try! While you can rest in the designated nap zones, judges will test your understanding of every line and architectural decision (Sections 3.4 & 5.1).",
        section_id="10-faq"
    )
]


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOCX_SEARCH_PATHS = [
    BASE_DIR / "data" / "Innovate_AI_Hackathon_Rulebook_DataSet.docx",
    BASE_DIR / "data" / "rulebook_dataset.docx",
    BASE_DIR / "data" / "rulebook.docx",
    BASE_DIR / "Innovate_AI_Hackathon_Rulebook_DataSet.docx",
    BASE_DIR / "rulebook_dataset.docx",
]


class KnowledgeBase:
    def __init__(self):
        self.docx_path = self._find_docx_file()
        self.chunks = DEFAULT_CHUNKS
        self.faqs = FAQ_LIST
        if self.docx_path:
            print(f"[RAG] Rulebook knowledge loaded from: {self.docx_path}")

    def _find_docx_file(self) -> Path | None:
        for path in DOCX_SEARCH_PATHS:
            if path.is_file():
                return path
        return None

    def get_chunks(self) -> list[dict[str, Any]]:
        return self.chunks

    def get_faqs(self) -> list[FAQItem]:
        return self.faqs

