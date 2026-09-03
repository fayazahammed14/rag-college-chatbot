import os
import sys
import asyncio
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Ensure server root is in python path
SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from app.config.db import get_supabase_client
from app.services.document_service import process_and_index_document, create_document

DOCS_DIR = SERVER_DIR / "sample_skcet_docs"
DOCS_DIR.mkdir(exist_ok=True)


def build_pdf(filename: str, title: str, sections: list) -> Path:
    """Generates a structured PDF with headers, paragraphs, and tables."""
    pdf_path = DOCS_DIR / filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#312e81'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=8
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph("Sri Krishna College of Engineering and Technology (SKCET) • Official Knowledge Publication", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6366f1'), spaceAfter=15))

    for sec_title, sec_content in sections:
        story.append(Paragraph(sec_title, h2_style))
        if isinstance(sec_content, list):
            for para in sec_content:
                story.append(Paragraph(para, body_style))
        else:
            story.append(Paragraph(sec_content, body_style))
        story.append(Spacer(1, 8))

    doc.build(story)
    print(f"Generated PDF: {pdf_path}")
    return pdf_path


def create_all_skcet_pdfs():
    """Generates all 6 comprehensive SKCET documents."""
    pdf_files = []

    # 1. Freshers, Admissions & Scholarships
    freshers_sections = [
        ("1. Institution Overview & Accreditation", [
            "Sri Krishna College of Engineering and Technology (SKCET), established in 1998, is an autonomous institution affiliated with Anna University, Chennai, and approved by AICTE, New Delhi. The college is located in Kuniamuthur, Coimbatore, Tamil Nadu.",
            "SKCET holds an 'A+' Grade accreditation from NAAC with high CGPA, NBA accreditation for all eligible undergraduate programs, and ranks consistently among the Top 100 engineering institutions in India according to the NIRF (National Institutional Ranking Framework) rankings.",
            "The official TNEA Counseling College Code for SKCET is 2722."
        ]),
        ("2. Programs Offered & Cutoff Insights", [
            "Undergraduate B.E. / B.Tech Programs (4 Years): Computer Science and Engineering (CSE), Information Technology (IT), Artificial Intelligence and Data Science (AI&DS), Computer Science and Business Systems (CSBS in partnership with TCS), Electronics and Communication Engineering (ECE), Electrical and Electronics Engineering (EEE), Mechanical Engineering (Mech), Mechatronics Engineering (MCT), and Civil Engineering (Civil).",
            "Postgraduate Programs: M.E. in Applied Electronics, Computer Science, Embedded Systems, CAD/CAM, Software Engineering, and 2-year full-time MBA (Master of Business Administration).",
            "Admission is conducted through Single Window TNEA counseling (Code 2722) based on 12th Standard HSC marks (Physics, Chemistry, Maths cutoff out of 200) and Management Quota based on merit."
        ]),
        ("3. Mandatory Certificates for Freshers Admission", [
            "Students reporting for admission must submit the following original documents along with 3 sets of photocopies:",
            "1. 10th and 12th Standard HSC Mark Sheets.<br/>2. TNEA Allotment Order and Fee Payment Receipt.<br/>3. Transfer Certificate (TC) and Conduct Certificate.<br/>4. Community Certificate (Permanent card for BC / BCM / MBC / DNC / SC / SCA / ST).<br/>5. First Graduate Certificate and Joint Declaration (if claiming First Graduate fee waiver).<br/>6. Nativity and Income Certificate (where applicable).<br/>7. Migration Certificate (for CBSE, ICSE, and other state board students).<br/>8. 6 Passport size photographs and Aadhaar Card copy."
        ]),
        ("4. Student Induction Programme (SIP) & Campus Life", [
            "All newly admitted 1st-year students participate in a mandatory 2-week Student Induction Programme (SIP) covering universal human values, campus familiarity, bridge courses in mathematics and programming, diagnostic assessments, creative arts, and physical health sessions.",
            "Each student is assigned a dedicated Faculty Mentor from their department who monitors academic performance, attendance, and personal well-being throughout the 4-year degree.",
            "Campus Dress Code: Formal attire with ID card worn at all times. On lab days, prescribed safety uniform (lab coats for workshops and chemistry labs) is mandatory."
        ]),
        ("5. Tuition Fees & Government Scholarships", [
            "Tuition Fees: For Government Quota (TNEA), tuition fee follows the official Tamil Nadu Fee Fixation Committee norm (~Rs. 50,000 to Rs. 55,000/year for non-accredited courses, ~Rs. 85,000/year for accredited autonomous courses). Management quota fees are as prescribed by the management council.",
            "First Graduate Scholarship: Eligible 1st-generation degree candidates receive an annual government fee concession of Rs. 25,000 directly waived from tuition fees.",
            "7.5% Government School Quota: Students who studied from 6th to 12th in Tamil Nadu Government schools receive 100% free education including tuition fees, hostel accommodation, and college bus transport funded by the Tamil Nadu Government.",
            "SC / ST / SCA Post-Matric Scholarship: Full tuition fee waiver for eligible students whose parental annual income is below Rs. 2.5 Lakhs.",
            "Sri Krishna Merit Scholarship: Offered by the management for sports achievers at national/state level and high-ranking academic achievers."
        ])
    ]
    p1 = build_pdf("SKCET_Freshers_Admissions_and_Scholarships_Guide.pdf", "SKCET Freshers, Admissions & Scholarships Handbook", freshers_sections)
    pdf_files.append((p1, "SKCET Freshers, Admissions & Scholarships Handbook"))

    # 2. Academic Regulations & Exams
    academic_sections = [
        ("1. Autonomous Regulations R2022 & Curriculum Structure", [
            "SKCET operates under the Autonomous Regulations R2022 and R2020. The curriculum is Choice Based Credit System (CBCS) designed with Outcome Based Education (OBE) principles aligned with Washington Accord standards.",
            "Total Credits for B.E. / B.Tech Degree: A student must earn approximately 160 to 165 credits across 8 semesters to qualify for the award of degree.",
            "Honors and Minor Degree: High-performing students with a minimum CGPA of 7.5 and no history of arrears can register for an additional 18 to 20 credits from Semester 4 to earn an 'Honors Degree' in specialized domains (e.g. B.E. CSE with Honors in AI) or a 'Minor Degree' in another discipline (e.g. B.E. Mechanical with Minor in Data Analytics)."
        ]),
        ("2. Attendance Requirements & Condonation Rules", [
            "Mandatory 75% Attendance: A candidate must secure a minimum of 75% overall attendance across all registered courses in a semester to be eligible to appear for the End-Semester Examinations.",
            "Medical Condonation: Attendance between 65% and 74% may be condoned by the Principal / Head of Institution on valid medical grounds, provided appropriate medical certificates and hospitalization records are submitted within 3 working days.",
            "Prevented / Redo Semester: Candidates securing less than 65% attendance are strictly prevented from appearing for the semester examinations, are deemed 'Detained', and must repeat / redo the entire semester in the subsequent academic year."
        ]),
        ("3. Assessment Pattern & Continuous Internal Evaluation (CIE)", [
            "Course Evaluation Weightage: 40% Continuous Internal Assessment (CIA) + 60% End-Semester Examination (ESE), or 50:50 for practical-integrated theory courses.",
            "Internal Assessment: Consists of Continuous Assessment Test 1 (CAT-1), Continuous Assessment Test 2 (CAT-2), model practical exams, digital assignments, mini-projects, and seminar/quiz assessments.",
            "Minimum Passing Criteria: A student must secure a minimum of 45% in the End-Semester Examination and 50% overall (CIA + ESE combined) to pass a course."
        ]),
        ("4. Grading System & CGPA Calculation", [
            "Letter Grades and Grade Points:<br/>"
            "• 'O' (Outstanding): 91-100 Marks (Grade Point: 10)<br/>"
            "• 'A+' (Excellent): 81-90 Marks (Grade Point: 9)<br/>"
            "• 'A' (Very Good): 71-80 Marks (Grade Point: 8)<br/>"
            "• 'B+' (Good): 61-70 Marks (Grade Point: 7)<br/>"
            "• 'B' (Average): 50-60 Marks (Grade Point: 6)<br/>"
            "• 'U' / 'RA' (Re-appear): <50 Marks (Grade Point: 0)<br/>"
            "• 'SA' (Shortage of Attendance / Detained): Grade Point 0",
            "GPA Formula: Sum of (Credit x Grade Point) divided by Sum of registered Credits in the semester.",
            "CGPA Formula: Cumulative Sum of (Credit x Grade Point) divided by Total Credits earned up to that semester."
        ]),
        ("5. Controller of Examinations (CoE) & Exam Grievances", [
            "End-Semester Examination Fees: Students must register through the CoE student portal and pay the prescribed fee per paper before the announced deadline.",
            "Revaluation & Answer Script Photocopy: Students unsatisfied with their grades can apply for transparent answer sheet photocopy within 7 days of result declaration. If discrepancies are found, they can apply for formal Revaluation.",
            "Fast-Track Scheme: Final year students with no standing arrears and high CGPA can complete their 8th semester elective credits in 6th/7th semester or via NPTEL/SWAYAM to undertake full-time 8-month industrial internships."
        ])
    ]
    p2 = build_pdf("SKCET_Academic_Regulations_and_Examination_Handbook.pdf", "SKCET Academic Regulations & Examination Handbook", academic_sections)
    pdf_files.append((p2, "SKCET Academic Regulations & Examination Handbook"))

    # 3. Hostel, Mess, Transport & Campus Life
    hostel_sections = [
        ("1. Hostel Accommodation & Facilities", [
            "SKCET provides state-of-the-art on-campus residential facilities for over 2,500 boys and girls in dedicated hostels: Venkata & Thirumalai Blocks (for Boys) and Sri Krishna & Ganga Blocks (for Girls).",
            "Room Options: 2-sharing, 3-sharing, and 4-sharing spacious furnished rooms with individual study tables, ergonomic chairs, wardrobes, and high-speed Wi-Fi access.",
            "Amenities: 24/7 uninterrupted power backup, solar hot water systems, modern gymnasium inside hostel blocks, indoor recreation rooms (table tennis, chess, carrom), and automated laundry facilities."
        ]),
        ("2. Hostel Timings, Curfew & Out-Pass System", [
            "Curfew & Attendance Roll Call: All hostellers must be inside the hostel premises by 6:30 PM (Girls Hostel) and 7:30 PM (Boys Hostel). Biometric attendance is taken daily between 8:00 PM and 8:30 PM.",
            "Digital Out-Pass & Leave System: Leave or outing requires prior application on the MySKCET hostel portal and automated SMS approval from the registered parent's mobile number.",
            "Study Hours: Mandatory silent study hours are observed between 8:30 PM and 10:30 PM daily."
        ]),
        ("3. Dining & Mess Services", [
            "The multi-cuisine dining hall serves hygienic, nutritious vegetarian and non-vegetarian meals prepared in steam-operated modern kitchens.",
            "Mess Timings:<br/>"
            "• Breakfast: 07:00 AM - 08:30 AM<br/>"
            "• Lunch: 12:30 PM - 01:45 PM<br/>"
            "• Evening Tea & Snacks: 04:30 PM - 05:30 PM<br/>"
            "• Dinner: 07:30 PM - 09:00 PM",
            "Special menu featuring South Indian, North Indian, and continental breakfast items with fresh milk, eggs, fruits, and weekly special feast on Sundays."
        ]),
        ("4. College Transport Fleet (Bus Routes)", [
            "SKCET operates an extensive fleet of over 65+ GPS-tracked air-conditioned and regular college buses covering major locations across Coimbatore, Tirupur, Erode, Pollachi, Mettupalayam, and Palakkad.",
            "Buses arrive on campus by 08:20 AM and depart at 05:00 PM (with extended special buses at 06:30 PM for students attending placement training, hackathon practice, and sports coaching).",
            "Transport registration and route selection are handled at the beginning of each academic year through the transport office."
        ]),
        ("5. Central Library (Dr. APJ Abdul Kalam Library)", [
            "The Central Library is an air-conditioned, fully automated Knowledge Resource Centre spread across 30,000 sq.ft with over 85,000 volumes, 25,000 titles, and national/international print journals.",
            "Working Hours: 08:00 AM to 08:00 PM on all working days, and 09:00 AM to 04:00 PM on Sundays during examination periods.",
            "Digital Library: 100+ multimedia terminals with round-the-clock access to IEEE Xplore, ScienceDirect, SpringerLink, ACM Digital Library, DELNET, NDL (National Digital Library), and NPTEL video lectures."
        ]),
        ("6. Health Centre & Emergency Contacts", [
            "A 24/7 on-campus Medical Centre with resident medical officers, certified nursing staff, and a dedicated emergency ambulance connected with Sri Ramakrishna Hospital and Ganga Hospital.",
            "First aid centers are stationed in every department block, workshop, and sports complex."
        ])
    ]
    p3 = build_pdf("SKCET_Hostel_Mess_Transport_and_Campus_Life.pdf", "SKCET Hostel, Mess, Transport & Campus Life Manual", hostel_sections)
    pdf_files.append((p3, "SKCET Hostel, Mess, Transport & Campus Life Manual"))

    # 4. Placement, Training & Career Guidance
    placement_sections = [
        ("1. Department of Training and Placement (DTP)", [
            "The Department of Training and Placement at SKCET is a premier career facilitation hub with a consistent track record of 95%+ campus placement for eligible graduates across engineering, technology, and management.",
            "Career Track Categorization:<br/>"
            "• Marquee Offers: Salary Package > Rs. 20 LPA (e.g. Amazon, Google, Microsoft, Atlassian)<br/>"
            "• Super Dream Offers: Salary Package between Rs. 10 LPA and Rs. 20 LPA (e.g. Zoho, Cisco, Walmart, Trimble, Virtusa Neural Hack)<br/>"
            "• Dream Offers: Salary Package between Rs. 5.5 LPA and Rs. 10 LPA (e.g. ThoughtWorks, Robert Bosch, Hexaware, Cognizant GenC Next)<br/>"
            "• Regular Offers: Salary Package up to Rs. 5.0 LPA (e.g. Accenture, TCS, Wipro, Capgemini, Infosys)",
            "Highest Salary Package: 44.0 LPA | Average Salary Package: 6.8 LPA"
        ]),
        ("2. Systematic 4-Year Placement Training Model", [
            "Semester 1 & 2: Communication Skills, Personality Development, Business English Certification (BEC), and Foundation in C & Python.",
            "Semester 3 & 4: Data Structures, Algorithms, Object-Oriented Programming (Java/C++), Quantitative Aptitude, and Logical Reasoning.",
            "Semester 5 & 6: Full Stack Web & Mobile Development, System Design, Competitive Coding on LeetCode/HackerRank, and Company-Specific Hackathons.",
            "Semester 7: Intensive Mock Technical Interviews, HR Simulation Rounds, Group Discussions, and Full-Day Corporate Bootcamps."
        ]),
        ("3. Placement Eligibility & Drive Policies", [
            "Eligibility Criteria: A minimum CGPA of 6.0 to 7.0 (varies by company) with no standing arrears at the time of the recruitment drive. Certain Tier-1 companies mandate 70%+ in 10th and 12th standards.",
            "Dream Upgrade Policy: A student placed in a Regular category company remains eligible to participate in Dream, Super Dream, and Marquee company recruitment drives until they secure a higher-tier offer.",
            "Offer Acceptance: Once a student receives a Dream or Super Dream offer, they are committed to that organization to allow fair opportunities for peers."
        ]),
        ("4. 8th Semester Full-Time Industrial Internship Policy", [
            "Students receiving internship offers with stipends exceeding Rs. 15,000/month during campus placements are permitted to undertake full-time 6-to-8 month industrial internships starting from January of their 8th semester.",
            "Semester 8 core project work is evaluated based on industrial deliverables, monthly progress reports, and joint review by the industry mentor and department faculty supervisor."
        ])
    ]
    p4 = build_pdf("SKCET_Placements_and_Career_Development_Handbook.pdf", "SKCET Placement, Training & Career Development Handbook", placement_sections)
    pdf_files.append((p4, "SKCET Placement, Training & Career Development Handbook"))

    # 5. Clubs, Hackathons & Student Achievements
    clubs_sections = [
        ("1. Hackathons & National Competitions (SIH Benchmark)", [
            "SKCET is widely celebrated across India for its monumental record in the Smart India Hackathon (SIH) organized by the Ministry of Education, Government of India, having won consecutive national championships and cash awards totaling lakhs of rupees.",
            "The college houses a 24x7 Hackathon Incubation Lab equipped with high-end GPU workstations, 3D printers, IoT hardware kits, and mentor rooms for prototype building.",
            "Internal Hackathons: The college hosts 'SKCET Innovate', 36-hour non-stop coding sprints, and industry-sponsored hackathons by Virtusa, Zoho, and AWS."
        ]),
        ("2. Active Technical Clubs & Professional Chapters", [
            "• Google Developer Student Clubs (GDSC SKCET): Workshops on Flutter, Cloud, AI, and Android.<br/>"
            "• SKCET Coding Club & Hack Club: Weekly competitive programming contests, algorithmic problem-solving.<br/>"
            "• Robotics & Mechatronics Society: Autonomous rover design, drone technology, line followers.<br/>"
            "• SAE India SKCET Collegiate Chapter: Designing BAJA, Supra, and Electric Vehicle (EV) race cars.<br/>"
            "• IEEE Student Branch & WIE (Women in Engineering): Technical paper presentations, international conferences.<br/>"
            "• ACM & CSI Student Chapters: Open-source software development and database hackathons."
        ]),
        ("3. Cultural Extravaganza — 'Dhruva' National Fest", [
            "Dhruva is the signature annual inter-collegiate cultural and technical festival of SKCET, hosting over 10,000+ student participants from engineering colleges across South India.",
            "Key Events: Western Music, Battle of Bands, Choreonite, Fashion Show, Gaming Tournaments (Valorant, BGMI, FIFA), RoboWars, Street Play, and Celebrity Concert Nights with renowned playback singers and artists."
        ]),
        ("4. Extension Activities & Social Responsibility", [
            "National Service Scheme (NSS): Village adoption, tree plantation drives, medical camps, rural literacy missions.<br/>"
            "National Cadet Corps (NCC): Army and Naval wing training with parade grounds, weapon training, and B/C Certificate exams.<br/>"
            "Youth Red Cross (YRC) & Rotaract Club: Blood donation drives (over 1,000 units donated annually) and disaster relief initiatives."
        ])
    ]
    p5 = build_pdf("SKCET_Student_Clubs_Hackathons_and_Events_Guide.pdf", "SKCET Student Clubs, Hackathons & Events Guide", clubs_sections)
    pdf_files.append((p5, "SKCET Student Clubs, Hackathons & Events Guide"))

    # 6. Alumni, Transcripts & Administrative Procedures
    alumni_sections = [
        ("1. SKCET Alumni Association (SKCETAA)", [
            "SKCET has a vibrant global network of over 30,000+ alumni working as software architects, founders, directors, civil servants, and researchers across Fortune 500 companies and universities worldwide.",
            "Global Alumni Chapters: Active alumni chapters in Silicon Valley (USA), United Kingdom, Singapore, Dubai (UAE), Bengaluru, Chennai, and Hyderabad.",
            "Alumni Mentorship: The 'Alumni Connect' portal enables current students to seek resume reviews, 1-on-1 career guidance, mock interviews, and referral opportunities from alumni in top tech companies."
        ]),
        ("2. Official Transcripts & WES Credential Evaluation", [
            "Application Procedure for Transcripts:<br/>"
            "1. Alumni and graduating students applying for higher studies abroad (MS / MBA) can request Official Academic Transcripts through the CoE portal (coe.skcet.ac.in).<br/>"
            "2. Required Documents: Scanned copies of all semester mark sheets, Consolidated Statement of Marks, and Degree Certificate.<br/>"
            "3. Processing Time: Official sealed and signed transcripts in tamper-evident envelopes are issued within 5 to 7 working days.",
            "Electronic Transcripts for WES / ICAS / IQAS: SKCET CoE is registered with World Education Services (WES) for direct electronic transcript transmission via secure portal."
        ]),
        ("3. Degree Certificates, Duplicate Marksheets & Verification", [
            "Degree Certificate Issuance: Official degree certificates are conferred by Anna University, Chennai during the Annual Graduation Day held on campus.",
            "Consolidated Marksheet & Provisional Certificate: Handed over to students within 30 days of completing the 8th semester and clearing all dues.",
            "Medium of Instruction (MOI) Certificate: Official certificate certifying English as the sole medium of instruction is issued by the Academic Registrar for visa and university applications.",
            "Duplicate Marksheet Procedure: In case of loss of original mark sheet, alumni must submit an FIR copy, non-traceable certificate from police, and prescribed fee to the Controller of Examinations."
        ]),
        ("4. Recommendation Letters & Academic Verification", [
            "Letters of Recommendation (LOR): Students seeking LORs for universities or fellowships must submit their academic resume, Statement of Purpose (SOP), and target university list to department professors at least 15 days in advance.",
            "Employment Background Verification (BGV): Third-party verification agencies (First Advantage, HireRight, AuthBridge) can verify alumni credentials by emailing official requests to the Controller of Examinations."
        ])
    ]
    p6 = build_pdf("SKCET_Alumni_Transcripts_and_Administrative_Guide.pdf", "SKCET Alumni, Transcripts & Administrative Guide", alumni_sections)
    pdf_files.append((p6, "SKCET Alumni, Transcripts & Administrative Guide"))

    return pdf_files


async def index_all_documents(pdf_files):
    """Indexes all generated PDFs into Supabase vector store with Gemini embeddings."""
    supabase = get_supabase_client()
    print("\n--- Starting Vector Indexing into Supabase & Gemini ---")

    for pdf_path, title in pdf_files:
        filename = pdf_path.name
        print(f"\nProcessing: {title} ({filename})...")
        with open(pdf_path, "rb") as f:
            file_bytes = f.read()

        # Check if already exists; if so, delete old one
        existing = supabase.table("documents").select("id").eq("title", title).execute()
        if existing.data and len(existing.data) > 0:
            for old_doc in existing.data:
                supabase.table("documents").delete().eq("id", old_doc["id"]).execute()
                print(f"Removed previous version of {title}")

        # Create new document
        doc_record = await create_document(
            title=title,
            filename=filename,
            uploader_id=None
        )
        doc_id = doc_record["id"]

        # Run extraction, chunking, and embedding
        await process_and_index_document(doc_id, file_bytes)
        print(f"[OK] Successfully indexed: {title} (ID: {doc_id})")

    print("\n[DONE] ALL SKCET DOCUMENTS SUCCESSFULLY INDEXED INTO CAMPUSMIND RAG!")


if __name__ == "__main__":
    files = create_all_skcet_pdfs()
    asyncio.run(index_all_documents(files))
