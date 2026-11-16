import os
from fpdf import FPDF
from docx import Document

OUTPUT_DIR = "sample_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_JD = """Senior Full-Stack & Backend Software Engineer
We are seeking a Backend / Full-Stack Software Engineer with 4+ years of experience building scalable microservices and cloud-native web applications.

Key Requirements:
- 4+ years of hands-on software engineering experience in Python or Java.
- Strong proficiency in FastAPI, Spring Boot, REST APIs, and Microservices architecture.
- Experience with PostgreSQL, SQL, and Redis for high-throughput data storage.
- Frontend familiarity with React.js and TypeScript.
- Hands-on deployment experience using Docker, Kubernetes, AWS, and CI/CD pipelines.
- Bachelor's degree (B.Tech / B.E. / B.S.) in Computer Science or related field.
"""

CANDIDATES = [
    (
        "Aarav_Sharma",
        "Aarav Sharma",
        "aarav.sharma@example.com",
        "+91-9876500101",
        "B.Tech in Computer Science",
        "5.5 years",
        "Senior Software Engineer with 5.5 years of experience designing scalable backend systems using Python, FastAPI, Java, and Spring Boot. Built event-driven Microservices on AWS with Docker, Kubernetes, PostgreSQL, Redis, and CI/CD. Developed internal dashboards in React.js and TypeScript.",
    ),
    (
        "Priya_Nair",
        "Priya Nair",
        "priya.nair@example.com",
        "+91-9876500102",
        "M.Tech in Software Systems",
        "4.5 years",
        "Full-Stack Engineer with 4.5 years of experience in Java, Spring Boot, React.js, TypeScript, and PostgreSQL. Architected REST APIs, Dockerized microservices, and automated CI/CD workflows on AWS.",
    ),
    (
        "Rohan_Verma",
        "Rohan Verma",
        "rohan.verma@example.com",
        "+91-9876500103",
        "B.E. in Information Technology",
        "4 years",
        "Backend Developer with 4 years of experience specializing in Python, FastAPI, Django, SQL, PostgreSQL, and Redis. Experienced with Docker, Linux, Git, and REST APIs.",
    ),
    (
        "Ananya_Das",
        "Ananya Das",
        "ananya.das@example.com",
        "+91-9876500104",
        "B.Tech in Computer Science",
        "3 years",
        "Software Engineer with 3 years of experience working with Java, Spring Boot, MySQL, and React.js. Familiar with Docker, GitHub Actions, and Agile/Scrum.",
    ),
    (
        "Vikram_Patel",
        "Vikram Patel",
        "vikram.patel@example.com",
        "+91-9876500105",
        "B.Sc in Computer Science",
        "6 years",
        "Cloud & Distributed Systems Engineer with 6 years of experience in Go, Python, Kubernetes, Docker, Terraform, AWS, Apache Kafka, and PostgreSQL.",
    ),
    (
        "Sneha_Kulkarni",
        "Sneha Kulkarni",
        "sneha.k@example.com",
        "+91-9876500106",
        "B.Tech in Electronics",
        "2.5 years",
        "Frontend Developer with 2.5 years of experience building responsive web apps using React.js, JavaScript, TypeScript, HTML5, CSS3, and Tailwind CSS.",
    ),
    (
        "Karthik_Reddy",
        "Karthik Reddy",
        "karthik.r@example.com",
        "+91-9876500107",
        "B.Tech in Computer Science",
        "5 years",
        "Enterprise Java Developer with 5 years of experience in Java, Spring Boot, Microservices, Oracle DB, SQL, Jenkins, and REST APIs.",
    ),
    (
        "Meera_Joshi",
        "Meera Joshi",
        "meera.joshi@example.com",
        "+91-9876500108",
        "M.S. in Data Science",
        "3.5 years",
        "AI/ML Engineer with 3.5 years of experience in Python, FastAPI, PyTorch, NLP, LangChain, RAG, Docker, and PostgreSQL.",
    ),
    (
        "Siddharth_Roy",
        "Siddharth Roy",
        "sid.roy@example.com",
        "+91-9876500109",
        "BCA in Computer Applications",
        "2 years",
        "Junior Full-Stack Developer with 2 years of experience using Node.js, Express.js, MongoDB, React.js, and JavaScript.",
    ),
    (
        "Neha_Gupta",
        "Neha Gupta",
        "neha.gupta@example.com",
        "+91-9876500110",
        "B.Tech in Computer Science",
        "4 years",
        "Backend Software Engineer with 4 years of experience in Python, FastAPI, Flask, PostgreSQL, Redis, Docker, AWS, and Pytest.",
    ),
    (
        "Aditya_Menon",
        "Aditya Menon",
        "aditya.m@example.com",
        "+91-9876500111",
        "MBA in Operations",
        "5 years",
        "IT Project Manager with 5 years of experience in Agile/Scrum, Jira, stakeholder management, and product roadmapping.",
    ),
    (
        "Divya_Sen",
        "Divya Sen",
        "divya.sen@example.com",
        "+91-9876500112",
        "B.Tech in Computer Science",
        "1.5 years",
        "Graduate Software Engineer with 1.5 years of experience in Python, SQL, Git, Linux, and basic React.js.",
    ),
]


def main():
    with open(os.path.join(OUTPUT_DIR, "sample_jd.txt"), "w", encoding="utf-8") as f:
        f.write(SAMPLE_JD)

    for idx, (slug, name, email, phone, edu, exp, summary) in enumerate(CANDIDATES):
        body = f"""{name}
Email: {email} | Phone: {phone}
Education: {edu}
Total Experience: {exp}

Professional Summary & Technical Experience
{summary}

Key Highlights
- Delivered production features with {exp} of industry experience.
- Collaborated in cross-functional Agile teams to optimize system latency and reliability.
"""
        if idx < 6:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=11)
            for line in body.splitlines():
                if line.strip():
                    pdf.multi_cell(180, 7, line)
                else:
                    pdf.ln(4)
            pdf.output(os.path.join(OUTPUT_DIR, f"{idx + 1:02d}_{slug}.pdf"))
        else:
            doc = Document()
            for line in body.splitlines():
                doc.add_paragraph(line)
            doc.save(os.path.join(OUTPUT_DIR, f"{idx + 1:02d}_{slug}.docx"))

    print(f"Generated 12 synthetic resumes (6 PDF, 6 DOCX) and sample_jd.txt in ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()