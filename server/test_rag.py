import asyncio
import sys
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVER_DIR))

from app.services.rag_service import answer_student_question


async def main():
    questions = [
        "What is the TNEA counseling code for SKCET and what scholarships are available for freshers?",
        "What are the hostel curfew timings and mess timings at SKCET?",
        "What is the highest and average salary package in placements, and who are the top recruiters?",
        "How can an alumnus apply for official transcripts and WES evaluation?"
    ]

    for q in questions:
        print("=" * 60)
        print("QUESTION:", q)
        answer, sources = await answer_student_question(q)
        print("\nANSWER:")
        print(answer)
        print("\nSOURCES:")
        for s in sources:
            print(f"- {s['document_title']} (Page {s['page_number']}, match {s.get('similarity')})")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
